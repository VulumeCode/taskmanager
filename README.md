# taskmanager

Python developer task

Create a REST API in Python for managing long running tasks with the following requirements:

- A task has a name, start date and status
- You need to be able to create, remove, edit and list tasks. (CRUD)
- Additionally, a task can be started and stopped/interrupted 
- A task has one of the following statuses:
    - Created: created and defined but not yet run
    - Running: currently being executed
    - Failed: finished but with error(s)
    - Successful: finished without errors
- The actual running of the task can be stubbed
- Secure the API with API key authentication and build API key management (creating, deleting and deactivating keys)
- Choose your backend storage technology and 3rd party libraries. Motivate your choice.
- Add some tests and a way to package and deploy your software as a Docker container.