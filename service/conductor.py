#!/usr/bin/env python3
"""
TODO: Reduce class duplication via https://fastapi.tiangolo.com/tutorial/extra-models/

"""

import os

from typing import List
from fastapi import FastAPI, HTTPException

from service.storage import StorageService, LocalStorage, EtcdStorage
from service.storage import StorageException

from service.models import Version
from service.models import ProjectCore, ProjectInput, Project
from service.models import ScenarioCore, ScenarioInput, Scenario
from service.models import ReservationCore, ReservationInput, Reservation


# Entry point for gunicorn (Dockerfile)
def select_storage():
    storage_type = os.environ.get("CONDUCTOR_STORAGE_TYPE", "ETCD")

    if storage_type == "LOCAL":
        print('Conductor using local storage')
        return StorageService(svc=LocalStorage())

    if storage_type == "ETCD":
        storage_host = os.environ.get('CONDUCTOR_STORAGE_HOST', 'localhost')
        storage_port = int(os.environ.get('CONDUCTOR_STORAGE_PORT', '2379'))

        etcd_storage = EtcdStorage(
            etcd_service=storage_host, etcd_port=storage_port
        )

        # Test connectivity here (add when I add lease support)

        print(f'Conductor using etcd: {storage_host}:{storage_port}')
        return StorageService(svc=etcd_storage)

    raise Exception('ETCD and LOCAL are only supported storage types')


def application():
    global storage_service
    global api
    global app_version

    api = FastAPI()
    storage_service = select_storage()
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


@api.post('/reserve/project/', response_model=Reservation)
def create_reservation(reservation: ReservationInput):
    try:
        result: Reservation = storage_service.create_reservation(reservation)
    except StorageException as err:
        raise HTTPException(
            status_code=err.status_code,
            detail=err.status_message
        )
    except Exception as err:
        print(err)
        raise HTTPException(status_code=400, detail='Generic failure')

    return result


@api.get('/reserve/project/', response_model=List[ReservationCore])
def get_all_reservations():
    try:
        summaries: List[ReservationCore] = storage_service.fetch_reservation()
    except StorageException as err:
        raise HTTPException(
            status_code=err.status_code,
            detail=err.status_message
        )
    except Exception as err:
        print(err)
        raise HTTPException(status_code=400, detail='Generic failure')

    return summaries


@api.get('/reserve/project/{project}', response_model=Reservation)
def get_reservation(name: str):
    try:
        reservation: Reservation = storage_service.fetch_reservation(name)
    except StorageException as err:
        raise HTTPException(
            status_code=err.status_code,
            detail=err.status_message
        )
    except Exception as err:
        print(err)
        raise HTTPException(status_code=400, detail='Generic failure')

    return reservation
