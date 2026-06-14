#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2026 Ivan Dodik
# SPDX-License-Identifier: AGPL-3.0-only

# Benchmark API response times on fresh Docker containers.
# Usage:
#   ./scripts/benchmark.sh before   # run BEFORE optimizations
#   ./scripts/benchmark.sh after    # run AFTER optimizations
#   ./scripts/benchmark.sh compare   # compare before/after results

set -euo pipefail

LABEL="${1:-before}"
RESULTS_DIR="$(dirname "$0")/../benchmark_results"
RESULTS_FILE="${RESULTS_DIR}/${LABEL}.txt"
BACKEND_URL="http://localhost:8000"
TIMEOUT=30

mkdir -p "$RESULTS_DIR"

# --- Functions ---

wait_for_backend() {
    echo "Waiting for backend to be ready..."
    local retries=0
    while ! curl -sf "${BACKEND_URL}/health" >/dev/null 2>&1; do
        retries=$((retries + 1))
        if [ "$retries" -gt 60 ]; then
            echo "ERROR: Backend did not start within 60 seconds"
            exit 1
        fi
        sleep 1
    done
    echo "Backend ready after ${retries}s"
}

get_jwt() {
    local response
    response=$(curl -sf -X POST "${BACKEND_URL}/api/auth/login" \
        -H "Content-Type: application/json" \
        -d '{"username":"admin","password":"admin123"}')
    echo "$response" | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])"
}

measure() {
    local label="$1"
    local method="$2"
    local url="$3"
    local token="$4"
    local body="${5:-}"

    local start end elapsed http_code
    start=$(python3 -c "import time; print(time.perf_counter())")

    if [ -n "$body" ]; then
        http_code=$(curl -sf -o /dev/null -w "%{http_code}" \
            -X "$method" "${BACKEND_URL}${url}" \
            -H "Authorization: Bearer ${token}" \
            -H "Content-Type: application/json" \
            -d "$body" \
            --max-time "$TIMEOUT" 2>/dev/null || echo "000")
    else
        http_code=$(curl -sf -o /dev/null -w "%{http_code}" \
            -X "$method" "${BACKEND_URL}${url}" \
            -H "Authorization: Bearer ${token}" \
            --max-time "$TIMEOUT" 2>/dev/null || echo "000")
    fi

    end=$(python3 -c "import time; print(time.perf_counter())")
    elapsed=$(python3 -c "print(f'{($end - $start) * 1000:.1f}')")

    printf "  %-45s %6s ms  HTTP %s\n" "$label" "$elapsed" "$http_code"
    echo "${label}|${elapsed}|${http_code}" >> "$RESULTS_FILE"
}

# --- Main ---

if [ "$LABEL" = "compare" ]; then
    if [ ! -f "${RESULTS_DIR}/before.txt" ] || [ ! -f "${RESULTS_DIR}/after.txt" ]; then
        echo "ERROR: Both before.txt and after.txt must exist in ${RESULTS_DIR}"
        exit 1
    fi
    echo ""
    echo "=== PERFORMANCE COMPARISON ==="
    echo ""
    printf "  %-45s %10s %10s %10s\n" "Endpoint" "BEFORE" "AFTER" "Delta"
    echo "  $(printf '%.0s-' {1..80})"

    paste -d'|' "${RESULTS_DIR}/before.txt" "${RESULTS_DIR}/after.txt" | while IFS='|' read -r b_label b_ms b_code a_label a_ms a_code; do
        label=$(echo "$b_label" | cut -d'|' -f1)
        b=$(echo "$b_ms" | cut -d'|' -f1)
        a=$(echo "$a_ms" | cut -d'|' -f1)
        delta=$(python3 -c "print(f'{float($b) - float($a):+.1f}')")
        pct=$(python3 -c "print(f'{(1 - float($a)/float($b)) * 100:+.0f}%' if float($b) > 0 else 'N/A')")
        printf "  %-45s %8s ms %8s ms %8s %s\n" "$label" "$b" "$a" "$delta" "$pct"
    done
    echo ""
    exit 0
fi

echo "=== BENCHMARK: ${LABEL} ===" | tee "$RESULTS_FILE"
echo "Started at: $(date)" | tee -a "$RESULTS_FILE"
echo "" | tee -a "$RESULTS_FILE"

# Clean start
echo "Stopping and removing old containers..."
cd "$(dirname "$0")/.."
docker compose down -v 2>/dev/null || true

echo "Building images..."
docker compose build 2>&1 | tail -5

echo "Starting db first..."
docker compose up -d db 2>&1 | tail -3
echo "Waiting for db to be healthy..."
sleep 3
until docker compose exec -T db pg_isready -U ct_user -d ct_database 2>/dev/null; do
    sleep 1
done
echo "Db is ready"

echo "Starting backend and bot..."
docker compose up -d backend telegram-bot 2>&1 | tail -3

wait_for_backend

echo "" | tee -a "$RESULTS_FILE"
echo "Getting JWT token..." | tee -a "$RESULTS_FILE"
TOKEN=$(get_jwt)
echo "Token obtained" | tee -a "$RESULTS_FILE"
echo "" | tee -a "$RESULTS_FILE"

echo "Running benchmarks..." | tee -a "$RESULTS_FILE"

# --- Benchmarks ---

echo "" >> "$RESULTS_FILE"
echo "[Tournament Detail]" >> "$RESULTS_FILE"
measure "GET /api/tournaments/1" "GET" "/api/tournaments/1" "$TOKEN"
measure "GET /api/tournaments/1/standings" "GET" "/api/tournaments/1/standings" "$TOKEN"
measure "GET /api/tournaments/1/games" "GET" "/api/tournaments/1/games?per_page=50" "$TOKEN"

echo "" >> "$RESULTS_FILE"
echo "[Player Endpoints]" >> "$RESULTS_FILE"
measure "GET /api/players?page=1&per_page=20" "GET" "/api/players?page=1&per_page=20" "$TOKEN"
measure "GET /api/players/1" "GET" "/api/players/1" "$TOKEN"
measure "GET /api/players/1/games" "GET" "/api/players/1/games" "$TOKEN"
measure "GET /api/players/1/tournaments" "GET" "/api/players/1/tournaments" "$TOKEN"

echo "" >> "$RESULTS_FILE"
echo "[Create Player]" >> "$RESULTS_FILE"
measure "POST /api/players (create)" "POST" "/api/players" "$TOKEN" '{"name":"Bench Test Player","rating":1500}'

echo "" >> "$RESULTS_FILE"
echo "[Stats & Other]" >> "$RESULTS_FILE"
measure "GET /api/stats" "GET" "/api/stats" "$TOKEN"
measure "GET /api/stats/head-to-head?player1=1&player2=2" "GET" "/api/stats/head-to-head?player1=1&player2=2" "$TOKEN"
measure "GET /api/favorites" "GET" "/api/favorites" "$TOKEN"

echo "" | tee -a "$RESULTS_FILE"
echo "=== BENCHMARK COMPLETE: ${LABEL} ===" | tee -a "$RESULTS_FILE"
echo "Results saved to: ${RESULTS_FILE}"

# Cleanup
echo "Stopping containers..."
docker compose down -v 2>/dev/null || true