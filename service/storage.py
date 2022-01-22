#!/usr/bin/env python3


import json
from typing import List

from etcd3gw.client import Etcd3Client
from etcd3gw.lease import Lease as Etcd3Lease

from service.models import Project, ProjectInput, ProjectCore
from service.models import ScenarioCore, ScenarioInput, Scenario
from service.models import ReservationCore, ReservationInput, Reservation
from service.models import ReservationEmail
from service.models import Lease


class StorageException(Exception):
    def __init__(self, status_code=500, status_message="Undefined"):
        Exception.__init__(self)
        self.status_code = status_code
        self.status_message = status_message


class ProjectNameNotFound(StorageException):
    def __init__(self, project_name):
        StorageException.__init__(
            self, status_code=404,
            status_message=f'Project {project_name} not found'
        )
        self.project_name = project_name


class ScenarioNameNotFound(StorageException):
    def __init__(self, scenario_name):
        StorageException.__init__(
            self, status_code=404,
            status_message=f'Scenario {scenario_name} not found'
        )
        self.scenario_name = scenario_name


class ReservationNameNotFound(StorageException):
    def __init__(self, reservation_name):
        StorageException.__init__(
            self, status_code=404,
            status_message=f'Reservation {reservation_name} not found'
        )
        self.reservation_name = reservation_name


class ReservationPermissionDenied(StorageException):
    def __init__(self, requester, owner):
        StorageException.__init__(
            self, status_code=401,
            status_message=f'You ({requester}) are not the owner ({owner}).'
        )
        self.requester = requester
        self.owner = owner


class Storage:
    def save_data(self):
        pass

    def load_data(self):
        pass

    def get_reservation(self, name, core=False):
        pass


class LocalStorage(Storage):
    def __init__(self, pathname="data", filename="local_storage.json"):
        self.data = {
            "project": {},
            "scenario": {}
        }

        self.storage_path = pathname
        self.storage_file = filename
        self.storage_name = f'{pathname}/{filename}'

        self.load_data()

    # Data handling routines
    def get_project(self, name, core=False):
        if name not in self.data["project"]:
            raise ProjectNameNotFound(name)

        if core:
            project = ProjectCore(
                name=name,
                title=self.data["project"][name]["title"]
            )
        else:
            project = Project(
                name=name,
                title=self.data["project"][name]["title"],
                description=self.data["project"][name]["description"]
            )

        return project

    def set_project(self, name, title, description):
        self.data["project"][name] = {
            "title": title,
            "description": description
        }

        # Fetch the project data, in schema format
        return self.get_project(name)

    def get_project_list(self) -> List[str]:
        return list(self.data["project"])

    def get_scenario(self, name, core=False):
        if name not in self.data["scenario"]:
            raise ScenarioNameNotFound(name)

        if core:
            scenario = ScenarioCore(
                name=name,
                title=self.data["scenario"][name]["title"],
                project=self.data["scenario"][name]["project"]
            )
        else:
            scenario = Scenario(
                name=name,
                title=self.data["scenario"][name]["title"],
                project=self.data["scenario"][name]["project"],
                description=self.data["scenario"][name]["description"]
            )

        return scenario

    def set_scenario(self, name, title, description, project):
        self.data["scenario"][name] = {
            "title": title,
            "description": description,
            "project": project
        }

        # Fetch the scenario data, in schema format
        return self.get_scenario(name)

    def get_scenario_list(self) -> List[str]:
        return list(self.data["scenario"])

    def save_data(self):
        # json the data and save to file
        with open(self.storage_name, "w") as outfile:
            json.dump(self.data, outfile)

    def load_data(self):
        # Load the data file if there.  Otherwise, start clean.
        try:
            with open(self.storage_name, "r") as infile:
                self.data = json.load(infile)
        except Exception:
            pass


class EtcdStorage(Storage):
    def __init__(
        self,
        etcd_service="localhost",
        etcd_port=2379
    ):

        self.storage_service = Etcd3Client(
            host=etcd_service, port=etcd_port, api_path='/v3/'
        )

    # Data handling routines
    def get_project(self, name, core=False):
        value = self.storage_service.get(f'/project/{name}')

        if not value:
            raise ProjectNameNotFound(name)

        data = json.loads(value[0])

        if core:
            project = ProjectCore(name=name, title=data["title"])
        else:
            project = Project(
                name=name, title=data["title"], description=data["description"]
            )

        return project

    def set_project(self, name, title, description):
        """
        Convert Python dictionary to string and store as value
        """

        data = {'title': title, 'description': description}

        self.storage_service.put(
            key=f'/project/{name}',
            value=json.dumps(data)
        )

        # Fetch the project data, in schema format
        return self.get_project(name)

    def get_project_list(self) -> List[str]:
        # Return list of (value, key metadata)
        results = self.storage_service.get_prefix('/project/')

        projects = [
            d["key"].decode("utf-8").split('/')[-1]
            for v, d in results
        ]

        return projects

    def get_scenario(self, name, core=False):
        value = self.storage_service.get(f'/scenario/{name}')

        if not value:
            raise ScenarioNameNotFound(name)

        data = json.loads(value[0])

        if core:
            scenario = ScenarioCore(
                name=name, title=data["title"], project=data["project"]
            )
        else:
            scenario = Scenario(
                name=name, title=data["title"], project=data["project"],
                description=data["description"]
            )

        return scenario

    def set_scenario(self, name, title, description, project):
        data = {
            "title": title,
            "description": description,
            "project": project
        }

        self.storage_service.put(
            key=f'/scenario/{name}',
            value=json.dumps(data)
        )

        # Fetch the scenario data, in schema format
        return self.get_scenario(name)

    def get_scenario_list(self) -> List[str]:
        # Return list of (value, key metadata)
        results = self.storage_service.get_prefix('/scenario/')

        scenarios = [
            d["key"].decode("utf-8").split('/')[-1]
            for v, d in results
        ]

        return scenarios

    def get_reservation_list(self) -> List[str]:
        # Fetch all reservation keys from etcd
        results = self.storage_service.get_prefix('/reservation/project/')

        reservations = [
            d["key"].decode("utf-8").split('/')[-1]
            for v, d in results
        ]

        return reservations

    def get_reservation(self, name: str, core: bool = False):
        """
        The returned TTL value is the time remaining on the reservation (calc).
        The storage service also retains the original requested duration.
        """

        value = self.storage_service.get(f'/reservation/project/{name}')

        if not value:
            raise ReservationNameNotFound(name)

        data = json.loads(value[0])

        if core:
            reservation = ReservationCore(
                project=name, email=data["email"]
            )
        else:
            lease = Etcd3Lease(int(data["id"]), client=self.storage_service)
            remaining = lease.ttl()

            reservation = Reservation(
                project=name, email=data["email"],
                id=int(data["id"]), ttl=remaining
            )

        return reservation

    def create_lease(self, duration: int) -> Lease:
        result = self.storage_service.lease(ttl=duration)

        return Lease(
            ttl=duration, id=result.id
        )

    def revoke_lease(self, id: int) -> bool:
        lease = Etcd3Lease(id, client=self.storage_service)

        if not lease.revoke():
            raise StorageException('Lease revocation failed')

        return True

    def set_reservation(self, project: str, email: str, duration: int):
        lease: Lease = self.create_lease(duration)

        data = {
            "email": email,
            "id": lease.id,
            "ttl": lease.ttl
        }

        self.storage_service.put(
            key=f'/reservation/project/{project}',
            value=json.dumps(data),
            lease=Etcd3Lease(lease.id, self.storage_service)
        )

        return self.get_reservation(project)


class StorageService:
    def __init__(self, svc=EtcdStorage()):
        self._svc = svc

    # Web service related calls
    def create_project(self, project: ProjectInput):

        try:
            self._svc.get_project(project.name)
        except ProjectNameNotFound:
            # This is okay for creating a project
            pass
        else:
            # This is not okay as it already exists
            raise StorageException(
                    status_code=409,
                    status_message=f'Project {project.name} exists'
            )

        # Project data, in Project schema format
        result_project = self._svc.set_project(
            project.name, project.title, project.description
        )

        self._svc.save_data()

        return result_project

    def fetch_project(self, name: str = None):
        """
        Dual purpose method
            - full detail result for specified project name
            - list of project summaries for unspecified project name
        """

        # Easy part - specific project request
        if name:
            # No error handling here as we want to pass them all back
            project: Project = self._svc.get_project(name)
            return project

        # Longer part - list of summaries
        project_list: List[str] = self._svc.get_project_list()

        return_projects: List[ProjectCore] = []
        for project in project_list:
            return_projects.append(
                self._svc.get_project(project, core=True)
            )

        return return_projects

    def create_scenario(self, scenario: ScenarioInput):

        # Are we creating a duplicate?
        try:
            self._svc.get_scenario(scenario.name)
        except ScenarioNameNotFound:
            # This is okay for creating a scenario
            pass
        else:
            # This is not okay as it already exists
            raise StorageException(
                    status_code=409,
                    status_message=f'Scenario {scenario.name} exists'
            )

        # Does project exist? (If not, pass not found exception back)
        self.fetch_project(scenario.project)

        # scenario data, in scenario schema format
        result_scenario = self._svc.set_scenario(
            scenario.name,
            scenario.title,
            scenario.description,
            scenario.project
        )

        self._svc.save_data()

        return result_scenario

    def fetch_scenario(self, name: str = None):
        """
        Dual purpose method
            - full detail result for specified scenario name
            - list of scenario summaries for unspecified scenario name
        """

        # Easy part - specific scenario request
        if name:
            # No error handling here as we want to pass them all back
            scenario: Scenario = self._svc.get_scenario(name)
            return scenario

        # Longer part - list of summaries
        scenario_list: List[str] = self._svc.get_scenario_list()

        return_scenarios: List[ScenarioCore] = []
        for scenario in scenario_list:
            return_scenarios.append(
                self._svc.get_scenario(scenario, core=True)
            )

        return return_scenarios

    def create_reservation(self, reservation: ReservationInput):
        """
        - Need to determine if an existing reservation exists, if so. Fail.
        - Creating a reservation requires:
          - Creating a Lease
          - Creating a Reservation entry with Lease info
        """

        # Assignment solely for PEP8
        project = reservation.project

        # Are we creating a duplicate?
        try:
            self._svc.get_reservation(project)
        except ReservationNameNotFound:
            # This is okay for creating a reservation
            pass
        else:
            # This is not okay as it already exists
            raise StorageException(
                    status_code=409,
                    status_message=f'Reservation for {project} exists'
            )

        # Create reservation bound to lease
        result_reservation: Reservation = self._svc.set_reservation(
            project=project,
            email=reservation.email, duration=reservation.duration
        )

        self._svc.save_data()

        return result_reservation

    def fetch_reservation(self, name: str = None):
        """
        Dual purpose method
            - full detail result for specified project name
            - list of reservation summaries for unspecified project name
        """

        # Easy part - specific reservation request
        if name:
            # No error handling here as we want to pass them all back
            result: Reservation = self._svc.get_reservation(name)
            return result

        # Longer part - list of summaries
        reservation_list: List[str] = self._svc.get_reservation_list()

        return_reservations: List[ReservationCore] = []
        for reservation in reservation_list:
            return_reservations.append(
                self._svc.get_reservation(reservation, core=True)
            )

        return return_reservations

    def delete_reservation(
        self, project: str, email: ReservationEmail
    ) -> bool:

        # Does the reservation exist?  If not, exception passed back up.
        result: Reservation = self._svc.get_reservation(project)

        # Only the owner can revoke it.
        if Reservation.email != email.email:
            raise ReservationPermissionDenied(
                email.email, Reservation.email
            )
        # Delete it by revoking the lease. Exception passed back up if fails
        return self._svc.revoke_lease(result.id)
