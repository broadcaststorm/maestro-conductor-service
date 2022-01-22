#!/usr/bin/env python3
"""
TODO: Reduce class duplication via https://fastapi.tiangolo.com/tutorial/extra-models/

"""

from typing import List
from fastapi import FastAPI, HTTPException

from service.storage import StorageService, StorageException

from service.models import Version
from service.models import ProjectCore, ProjectInput, Project
from service.models import ScenarioCore, ScenarioInput, Scenario


# Entry point for gunicorn (Dockerfile)
def application():
    global storage_service
    global api
    global app_version

    api = FastAPI()
    storage_service = StorageService()
    app_version = Version(version='0.2.0')

    return api


# Entry point for uvicorn (local)
app = application()


@api.get('/version', response_model=Version)
def version():
    return app_version


@api.get('/project/', response_model=List[ProjectCore])
def get_all_projects():
    try:
        summaries: List[ProjectCore] = storage_service.fetch_project()
    except StorageException as err:
        raise HTTPException(
            status_code=err.status_code,
            detail=err.status_message
        )
    except Exception as err:
        print(err)
        raise HTTPException(status_code=400, detail='Generic failure')

    return summaries


@api.post('/project/', response_model=Project)
def create_project(project: ProjectInput):
    # FastAPI will return 422? if there's data validation issues

    try:
        result = storage_service.create_project(project)
    except StorageException as err:
        raise HTTPException(
            status_code=err.status_code,
            detail=err.status_message
        )
    except Exception as err:
        print(err)
        raise HTTPException(status_code=400, detail='Generic failure')

    return result


@api.get('/project/{name}', response_model=Project)
def get_project(name: str):

    try:
        project = storage_service.fetch_project(name)
    except StorageException as err:
        raise HTTPException(
            status_code=err.status_code,
            detail=err.status_message
        )
    except Exception as err:
        print(err)
        raise HTTPException(status_code=400, detail='Generic failure')

    return project


@api.get('/scenario/', response_model=List[ScenarioCore])
def get_all_scenarios():
    try:
        summaries: List[ScenarioCore] = storage_service.fetch_scenario()
    except StorageException as err:
        raise HTTPException(
            status_code=err.status_code,
            detail=err.status_message
        )
    except Exception as err:
        print(err)
        raise HTTPException(status_code=400, detail='Generic failure')

    return summaries


@api.post('/scenario/', response_model=Scenario)
def create_scenario(scenario: ScenarioInput):
    try:
        result: Scenario = storage_service.create_scenario(scenario)
    except StorageException as err:
        raise HTTPException(
            status_code=err.status_code,
            detail=err.status_message
        )
    except Exception as err:
        print(err)
        raise HTTPException(status_code=400, detail='Generic failure')

    return result


@api.get('/scenario/{name}', response_model=Scenario)
def get_scenario(name: str):

    try:
        scenario: Scenario = storage_service.fetch_scenario(name)
    except StorageException as err:
        raise HTTPException(
            status_code=err.status_code,
            detail=err.status_message
        )
    except Exception as err:
        print(err)
        raise HTTPException(status_code=400, detail='Generic failure')

    return scenario
