@echo off
protoc --csharp_out=../api/Api/Proto/ --python_out=./python/ v1/ProtoBot.proto
