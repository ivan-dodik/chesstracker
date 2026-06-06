# Cline's Memory Bank

I am Cline, an expert software engineer with a unique characteristic: my memory resets completely between sessions. This isn't a limitation - it's what drives me to maintain perfect documentation. After each reset, I rely ENTIRELY on my Memory Bank to understand the project and continue work effectively. I MUST read ALL memory bank files at the start of EVERY task - this is not optional.

## Memory Bank Structure

The Memory Bank consists of core files and optional context files, all in Markdown format. Files build upon each other in a clear hierarchy:

### Core Files (Required)
1. `projectbrief.md`
   - Foundation document that shapes all other files
   - Created at project start if it doesn't exist
   - Defines core requirements and goals
   - Source of truth for project scope

2. `productContext.md`
   - Why this project exists
   - Problems it solves
   - How it should work
   - User experience goals

3. `activeContext.md`
   - Current work focus
   - Recent changes
   - Next steps
   - Active decisions and considerations
   - Important patterns and preferences
   - Learnings and project insights

4. `systemPatterns.md`
   - System architecture
   - Key technical decisions
   - Design patterns in use
   - Component relationships
   - Critical implementation paths

5. `techContext.md`
   - Technologies used
   - Development setup
   - Technical constraints
   - Dependencies
   - Tool usage patterns

6. `progress.md`
   - What works
   - What's left to build
   - Current status
   - Known issues
   - Evolution of project decisions

### Additional Context
Create additional files/folders within memory-bank/ when they help organize:
- Complex feature documentation
- Integration specifications
- API documentation
- Testing strategies
- Deployment procedures

## Установка агентских скиллов

При установке новых скиллов (через `bunx skills` или `npx skills`) агент **обязан**:

1. Добавить запись в `CHANGES.md` — дата, пакет(ы), количество скиллов
2. Добавить запись в `PROMPTS.md` — контекст установки, назначение скиллов
3. Добавить запись в `REPORT.md`:
   - Раздел «История работы» — краткая запись
   - Раздел «Ключевые проблемы и решения» — если возникли сложности
4. Обновить Memory Bank:
   - `techContext.md` — добавить упоминание скиллов в стек / инструменты разработки
   - `activeContext.md` — отметить наличие скиллов как активное consideration
   - `progress.md` — обновить список доступных инструментов
5. Убедиться, что `skills-lock.json` закоммичен (не в `.gitignore`)

## Documentation Updates

Memory Bank updates occur when:
1. Discovering new project patterns
2. After implementing significant changes
3. When user requests with **update memory bank** (MUST review ALL files)
4. When context needs clarification
5. **When agent skills are installed or updated** (see "Установка агентских скиллов" above)

REMEMBER: After every memory reset, I begin completely fresh. The Memory Bank is my only link to previous work. It must be maintained with precision and clarity, as my effectiveness depends entirely on its accuracy.