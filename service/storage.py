#!/usr/bin/env python3


import json
from typing import List

from service.models import Project, ProjectInput, ProjectCore
from service.models import ScenarioCore, ScenarioInput, Scenario


class StorageException(Exception):
    def __init__(self, status_code=500, status_message='Undefined'):
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


class StorageService:
    # For PoC, let's start with local storage
    def __init__(self, pathname='data', filename='local_storage.json'):
        self.data = {
            "project": {},
            "scenario": {}
        }

        self.storage_path = pathname
        self.storage_file = filename
        self.storage_name = f'{pathname}/{filename}'


    # Data handling routines
    def _get_project(self, name, core=False):
        if name not in self.data["project"]:
            raise ProjectNameNotFound(name)

        if core:
            project = ProjectCore(
                name=name,
                title=self.data["project"][name]['title']
            )
        else:
            project = Project(
                name=name,
                title=self.data["project"][name]['title'],
                description = self.data["project"][name]['description']
            )

        return project


    def _set_project(self, name, title, description):
        self.data["project"][name] = {
            'title': title,
            'description': description
        }

        # Fetch the project data, in schema format
        return self._get_project(name)


    def _get_project_list(self) -> List[str]:
        return list(self.data["project"])


    def _get_scenario(self, name, core=False):
        if name not in self.data["scenario"]:
            raise ScenarioNameNotFound(name)

        if core:
            scenario = ScenarioCore(
                name=name,
                title=self.data["scenario"][name]['title'],
                project=self.data["scenario"][name]['project']
            )
        else:
            scenario = Scenario(
                name=name,
                title=self.data["scenario"][name]['title'],
                project=self.data["scenario"][name]['project'],
                description = self.data["scenario"][name]['description']
            )

        return scenario


    def _set_scenario(self, name, title, description, project):
        self.data["scenario"][name] = {
            'title': title,
            'description': description,
            'project': project
        }

        # Fetch the scenario data, in schema format
        return self._get_scenario(name)


    def _get_scenario_list(self) -> List[str]:
        return list(self.data["scenario"])


    def save_data(self):
        # json the data and save to file
        with open(self.storage_name, 'w') as outfile:
            json.dump(self.data, outfile)


    def load_data(self):
        # Load the data file if there.  Otherwise, start clean.
        try:
            with open(self.storage_name, 'r') as infile:
                self.data = json.load(infile)
        except:
            pass


    # Web service related calls
    def create_project(self, project: ProjectInput):

        try:
            self._get_project(project.name)
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
        result_project = self._set_project(
            project.name, project.title, project.description
        )

        self.save_data()

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
            project: Project = self._get_project(name)
            return project
        
        # Longer part - list of summaries
        project_list: List[str] = self._get_project_list()

        return_projects: List[ProjectCore] = []
        for project in project_list:
            return_projects.append(
                self._get_project(project, core=True)
            )

        return return_projects

    def create_scenario(self, scenario: ScenarioInput):

        # Are we creating a duplicate?
        try:
            self._get_scenario(scenario.name)
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
        result_scenario = self._set_scenario(
            scenario.name,
            scenario.title,
            scenario.description,
            scenario.project
        )

        self.save_data()

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
            scenario: Scenario = self._get_scenario(name)
            return scenario
        
        # Longer part - list of summaries
        scenario_list: List[str] = self._get_scenario_list()

        return_scenarios: List[ScenarioCore] = []
        for scenario in scenario_list:
            return_scenarios.append(
                self._get_scenario(scenario, core=True)
            )

        return return_scenarios

    pass
