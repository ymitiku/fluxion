# Feature Branch Guidelines for Fluxion Releases

This document outlines standardized guidelines for managing feature branches during Fluxion releases. Following these practices ensures consistency, quality, and streamlined collaboration for all feature releases.

---

## **1. Branch Naming Conventions**

Feature branch names should follow a consistent and descriptive naming pattern:

- **Feature Branches**:
  ```
  feature/<feature-name>
  ```
  Example: `feature/planning-agent`

- **Bug Fixes**:
  ```
  fix/<bug-name>
  ```
  Example: `fix/incorrect-tool-call`

- **Maintenance Tasks**:
  ```
  chore/<task-name>
  ```
  Example: `chore/update-readme`

---

## **2. Branch Creation Workflow**

1. **Checkout the Release Branch**:
   ```bash
   git checkout release/<release-version>
   ```
   Example:
   ```bash
   git checkout release/v1.0.0
   ```

2. **Create a New Feature Branch**:
   ```bash
   git checkout -b feature/<feature-name>
   ```
   Example:
   ```bash
   git checkout -b feature/planning-agent
   ```

3. **Push the Branch to Remote**:
   ```bash
   git push -u origin feature/<feature-name>
   ```
   Example:
   ```bash
   git push -u origin feature/planning-agent
   ```

---

## **3. Feature Development Workflow**

1. **Incremental Commits**:
   - Break changes into small, logical commits with clear messages.
   - Example Commit Messages:
     - `Add base class for PlanningAgent`
     - `Implement generate_plan method`
     - `Write unit tests for PlanningAgent`

2. **Unit Tests**:
   - Write unit tests for all new functionality.

3. **Documentation**:
   - Update relevant documentation (e.g., README, API reference).

4. **Code Quality**:
   - Run linters (e.g., `flake8`) and formatters (e.g., `black`) before pushing.

5. **Push Regularly**:
   - Push commits frequently to avoid conflicts and keep backups of your work.

---

## **4. Review and Merge Workflow**

1. **Open a Pull Request**:
   - Create a PR targeting the release branch (e.g., `release/v1.0.0`).
   - Use the following template:

     ```markdown
     ### Feature: <Feature Name>

     **Description:**
     - <Brief summary of the feature>

     **Changes:**
     - <List of changes in the codebase>

     **Testing:**
     - <Steps taken to test the feature or linked test cases>
     ```

2. **Review Process**:
   - Ensure at least one code review is completed before merging.
   - Address any feedback promptly.

3. **Squash Merge into Release Branch**:
   - Use squash merges to keep the release branch history clean.
   ```bash
   git checkout release/<release-version>
   git merge --squash feature/<feature-name>
   git commit -m "Add <feature-name> functionality"
   ```

4. **Delete the Feature Branch**:
   ```bash
   git branch -d feature/<feature-name>
   git push origin --delete feature/<feature-name>
   ```

---

## **5. Feature Description Template**

**Feature Overview:**
- **Name:** `<Feature Name>`
- **Objective:** `<What the feature is intended to accomplish>`
- **Dependencies:** `<List of tools/agents/workflows this feature depends on>`
- **Planned Actions:** `<Breakdown of steps or tasks involved in the feature>`

**Example:**
```markdown
### Feature: PlanningAgent

**Objective:**
- Implement a PlanningAgent capable of generating and executing task plans using tool and agent calls.

**Dependencies:**
- ToolRegistry for invoking tools dynamically.
- AgentCallingWrapper for invoking agents.

**Planned Actions:**
1. Add base class for PlanningAgent.
2. Implement generate_plan method to parse LLM-generated plans.
3. Add execute_plan method with support for retries and error recovery.
4. Write unit tests for PlanningAgent methods.
```

---

## **6. Checklist for Feature Completion**

Before merging, ensure the following checklist is met:

1. **Code Quality:**
   - Code is linted and formatted.
   - All unit tests pass locally and in CI/CD pipelines.

2. **Documentation:**
   - Feature is documented in README or API reference.
   - Examples or usage guides are updated (if applicable).

3. **Testing:**
   - Unit and integration tests cover the new feature.
   - Edge cases and error scenarios are handled.

4. **Review:**
   - PR is reviewed and approved by at least one team member.

---

## **7. Best Practices**

- **Communication:**
  - Keep your team informed about the status of your feature branch.

- **Small Iterations:**
  - Avoid large, monolithic changes. Break work into smaller, manageable tasks.

- **Frequent Syncs:**
  - Regularly pull updates from the release branch to avoid conflicts.

---

This standardized approach ensures that all feature branches contribute effectively to the stability and quality of each Fluxion release.

