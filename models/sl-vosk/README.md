# VOSK

## CONFIG
- Shortcode: ` vs `
- Docker: ` ghcr.io/robmsmt/speechloop/sl-vosk-en-16k:latest `
- Website: http://alphacephei.com
- Github: https://github.com/alphacep/vosk-api
- Type: ` DNN-WFST - Kaldi based trained model with modifications `
- Licence: ` Open Source - Apache-2.0 Licence `
- InternalPort: ` 2700 `
- ExternalPort: ` 2800 `
- SampleRate: ` 16000 `
- InterfaceType: ` docker-websocket `

## CHANGES
 - Took the [original image](alphacep/vosk-api), swapped out for the smaller 16k SR model image.
 - Installed websocat to allow for image healthcheck if it fails it'll reboot
