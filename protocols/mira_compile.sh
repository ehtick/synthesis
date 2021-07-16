#!/bin/bash
protoc -I=../mirabuf --csharp_out=../api/Mirabuf ../mirabuf/*.proto

