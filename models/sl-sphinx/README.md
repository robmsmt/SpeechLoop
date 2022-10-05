# SPHINX

## CONFIG
- Shortcode: ` sp `
- Docker: ` ghcr.io/robmsmt/speechloop/sl-sphinx-en-16k:latest `
- InternalPort: ` 3000 `
- ExternalPort: ` 3000 `
- SampleRate: ` 16000 `
- InterfaceType: ` docker-fastapi `

## CHANGES
 - Took the original python application (built with swig libalsa etc in docker image)
 - Installed fast_api / curl for healthcheck
