# DASS Assignment 2: Software Testing - Task Breakdown

Based on `DASS Assignment 2.pdf` and the `QuickCart System.md` API documentation, here is a detailed, step-by-step breakdown of everything you need to do for this assignment.

## General Requirements
*   **Individual Assignment**: You must work on this alone.
*   **Git Version Control**: 
    *   Create a Git repository right away.
    *   Push your work after completing each sub-question.
    *   Ensure all commits have clear, meaningful messages (this is graded).
*   **Testing Framework**: Use `pytest` for all test cases.
*   **AI Policy**: Usage of AI will be heavily penalized. Do not use AI to generate the code or diagrams.
*   **Diagrams**: Must be hand-drawn and photographed clearly.
*   **Code**: All provided or written code must run properly.

---

## Part 1: White Box Testing (25 Marks)
**Target**: The provided `moneypoly` board game code.

1.  **Control Flow Graph (CFG)**
    *   Draw a Control Flow Graph for the `moneypoly` program *by hand*.
    *   Every node must represent a statement or block of statements and be clearly labeled; arrows must show control flow.
    *   Take a clear photo and attach it to your white-box testing report.
2.  **Code Quality Analysis**
    *   Run `pylint` on the `moneypoly` codebase.
    *   Iteratively fix the warnings and suggestions provided by `pylint`.
    *   **Commit Format**: For each iteration of fixes, commit with the message format: `Iteration #: <What You Changed>`.
    *   Document all of these changes in your report.
3.  **White Box Test Cases**
    *   Write `pytest` test cases based on the internal structure of the `moneypoly` code.
    *   **Coverage requirements**: All branches/decision paths, key variable states, and edge cases (e.g., zero values, large inputs).
    *   **Report**: Explain in simple words why each test is needed, and detail any errors/logical issues found.
    *   **Fixing & Committing**: Correct the source code for each error you find. Commit these fixes using the format: `Error #: <What You Changed>`.

---

## Part 2: Integration Testing (40 Marks)
**Target**: Design, build, and test a command-line "StreetRace Manager" system from scratch.

1.  **System Implementation**
    *   Build the system module-by-module, committing each component to Git before integrating.
    *   **Required Modules**: Registration, Crew Management, Inventory, Race Management, Results, Mission Planning.
    *   **Extra Modules**: Design and implement at least **two additional modules** of your choice.
    *   Implement sensible business rules (e.g., drivers must be registered, inventory updates based on race results, mechanics must be available for damaged cars).
2.  **Call Graph**
    *   Draw a Call Graph showing all function calls within and between modules *by hand*.
    *   Nodes = functions; Arrows = calls. Clearly show inter-module calls.
    *   Take a photo and add it to your integration testing report.
3.  **Integration Test Design**
    *   Write test cases validating interactions between the different modules (referencing your Call Graph).
    *   **Report**: Document the scenario tested, modules involved, expected result, actual result, and any errors/logical issues found and fixed. Explain why each case is needed in simple language.

---

## Part 3: Black Box API Testing (35 Marks)
**Target**: The `QuickCart` REST API, using the `QuickCart System.md` documentation.

1.  **Setup the Server**
    *   Install Docker.
    *   Load the provided image: `docker load -i quickcart_image.tar`
    *   Run the server: `docker run -p 8080:8080 quickcart`
2.  **Test Case Design**
    *   Design comprehensive black-box tests using inputs derived explicitly from the `QuickCart System.md` documentation (e.g., headers like `X-Roll-Number`, bounds checks like name length 2-50 characters, address payload schemas, etc.).
    *   Coverage must include: Valid requests, invalid inputs, missing fields, wrong data types, and boundary values.
    *   **Report**: List each test case with its input, expected output, and a justification for why it's important.
3.  **Automated Testing**
    *   Use `pytest` and the Python `requests` library to automate these tests against the running Docker endpoint.
    *   Verify: Correct HTTP status codes, exact JSON response structures, and correctness of returned data.
4.  **Bug Report**
    *   For every bug you discover in the QuickCart API, document it in your report.
    *   Each bug report must include: Endpoint tested, Request payload (method, URL, headers, body), Expected result (per the MD doc), and Actual observed result.

---

## Submission Format
You must structure your GitHub Repository and your final `.zip` file exactly as follows:

```text
<rollnumber>/
├── README.md                 <-- Must include instructions on how to run tests/code and a link to your Git repo.
├── whitebox/
│   ├── diagrams/             <-- Hand-drawn CFG images
│   ├── tests/                <-- pytest files for moneypoly
│   └── report.pdf            <-- pylint docs, test justifications, bug fixes
├── integration/
│   ├── diagrams/             <-- Hand-drawn Call Graph images
│   ├── tests/                <-- Integration test cases
│   ├── code/                 <-- Source code for StreetRace Manager
│   └── report.pdf            <-- Extra modules explanation, test scenarios, actual vs expected results
└── blackbox/
    ├── tests/                <-- pytest & requests scripts for QuickCart
    └── report.pdf            <-- Test case lists, justifications, and detailed Bug Reports
```

**Final Step**: Compress the `<rollnumber>` folder into `<RollNumber>.zip` and submit it on Moodle before **23 March 2026**. Make sure your Git repository mirrors this structure.