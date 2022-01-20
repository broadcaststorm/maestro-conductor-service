# Maestro Application: Conductor Web Service

Web service that provides REST API interface to automate project and
scenario deployments in the Maestro lab orchestration system.

The REST API framework leveraged here is FastAPI, leveraging Pythonic
technologies to define the API and Schema to autogenerate the OpenAPI
spec and docs (OpenAPI-UI and Redocly versions).

## Pre-Requisites

- [FastAPI](https://fastapi.tiangolo.com)
- [Pydantic](https://pydantic-docs.helpmanual.io/)
- [Uvicorn](https://www.uvicorn.org), [GitHub](https://github.com/encode/uvicorn)
- [validators](https://validators.readthedocs.io), [GitHub](https://github.com/kvesteri/validators)
- [Requests](https://docs.python-requests.org/en/latest/)

## Related Documentation

- [HTTP Status Codes from MDN](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status)
- [Python Requests request class attribute: data vs json](https://stackoverflow.com/questions/26615756/python-requests-module-sends-json-string-instead-of-x-www-form-urlencoded-param)
- [Dockerfile reference](https://docs.docker.com/engine/reference/builder/)
- [etcd 3.5 docs](https://etcd.io/docs/v3.5/)
- [etcd3-gateway](https://docs.openstack.org/etcd3gw/latest/), [OpenDev Repo](https://opendev.org/openstack/etcd3gw)
- [Rancher Desktop Mac Networking Issue](https://github.com/rancher-sandbox/rancher-desktop/issues/1141)

## Roadmap Items

- Authentication
