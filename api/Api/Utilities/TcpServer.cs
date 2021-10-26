﻿using System;
using System.Collections.Generic;
using System.Text;
using System.Net;
using System.Net.Sockets;
using System.Reflection;
using System.IO;
using System.Threading;
using System.Threading.Tasks;
using System.Linq;
using Google.Protobuf;
using ProtoBuf;
using System.Collections.Concurrent;
using SynthesisAPI.Simulation;
using UnityEngine;

namespace SynthesisAPI.Utilities
{

    public static class TcpServerManager
    {
        private sealed class Server
        {
            private Socket _server = new Socket(AddressFamily.InterNetwork, SocketType.Stream, ProtocolType.Tcp);
            private const int _port = 13000;
            private List<ClientState> _clients = new List<ClientState>();
            private byte[] _buffer = new byte[1024];

            //private List<ClientHandler> clients;
            //public TcpListener listener;
            //public Thread listenerThread;
            public Thread clientManagerThread;
            public Thread writerThread;
            private bool _isRunning;
            public bool _canAcceptClients;
            //private List<Task> _currentWrites;
            public bool IsRunning
            {
                get => _isRunning;
                set
                {
                    _isRunning = value;
                    if (!value)
                    {
                        if (/*listenerThread != null && listenerThread.IsAlive*/true)
                        {
                            //listener.Stop();
                            //listenerThread.Join();
                            clientManagerThread.Join();
                            writerThread.Join();
                        }
                    }
                    if (value)
                    {
                        Start();
                    }
                }
            }


            private class ClientHandler
            {
                public ClientState state;
                public NetworkStream stream;
                public Task<ConnectionMessage?>? message;
                public TcpClient client;
                public List<ControllableState> currentResources;
            }

            /*
            private class ClientState
            {
                public bool IsConnected { get; set; } = false;
                public string? ResourceName { get; set; }
                public long LastHeartbeat { get; set; }
            }
            */


            private static readonly Lazy<Server> lazy = new Lazy<Server>(() => new Server());
            public static Server Instance { get { return lazy.Value; } }
            private Server()
            {
                //listener = new TcpListener(IPAddress.Parse("127.0.0.1"), 13000);
                _isRunning = false;
                _canAcceptClients = false;
                //_currentWrites = new List<Task>();
            }

            
            struct ClientState
            {
                public Socket socket;
                public byte[] buffer;
            }
            

            private void AcceptCallback(IAsyncResult asyncResult)
            {
                ClientState client = new ClientState
                {
                    socket = _server.EndAccept(asyncResult),
                    buffer = new byte[1024]
                };
                _clients.Add(client);
                if (_isRunning)
                {
                    _server.BeginReceive(_buffer, 0, _buffer.Length, SocketFlags.None, new AsyncCallback(AcceptCallback), client);
                    _server.BeginAccept(new AsyncCallback(ReceiveCallback), null);
                }
            }

            private void ReceiveCallback(IAsyncResult asyncResult)
            {
                ClientState client = (ClientState)asyncResult.AsyncState;
                int received = client.socket.EndReceive(asyncResult);
                ConnectionMessage.Parser.ParseDelimitedFrom(new MemoryStream(client.buffer, 0, received));
            }

            public void Start()
            {
                _server.Bind(new IPEndPoint(IPAddress.Any, _port));
                _server.Listen(5);
                _server.BeginAccept(new AsyncCallback(AcceptCallback), null);
                Logger.Log("Starting TCP Server", LogLevel.Debug);
                // use 1024 byte buffer
                //clients = new List<ClientHandler>();
                //listener.Start();
                _canAcceptClients = true;

                /*
                listenerThread = new Thread(() =>
                {
                    while (_isRunning)
                    {
                        try
                        {
                            TcpClient cli = (listener.AcceptTcpClient());
                            NetworkStream ns = cli.GetStream();

                            clients.Add(new ClientHandler
                            {
                                client = cli,
                                stream = ns,
                                message = ParseMessageAsync(ns),
                                currentResources = new List<ControllableState>(),
                                state = new ClientState()
                                {
                                    LastHeartbeat = DateTimeOffset.Now.ToUnixTimeMilliseconds()
                                }
                            });
                        }
                        catch (SocketException)
                        {
                            Logger.Log("TCP Listener stopped succesfully.", LogLevel.Debug);
                        }
                    }
                });
                */
                /*
                clientManagerThread = new Thread(() =>
                {
                    while (_isRunning || clients.Any())
                    {
                        if (!_isRunning)
                        {
                            for (int i = clients.Count - 1; i >= 0; i--)
                            {
                                RemoveClient(clients[i]);
                            }
                        }
                        for (int i = clients.Count - 1; i >= 0; i--)
                        {
                            if (clients[i].message != null)
                                System.Diagnostics.Debug.WriteLine(clients[i].message.IsCompleted);
                            if (DateTimeOffset.Now.ToUnixTimeMilliseconds() - clients[i].state.LastHeartbeat > 7000 && clients[i].message != null && clients[i].message.IsCompleted)
                            {
                                if (!RemoveClient(clients[i]))
                                {
                                    Logger.Log("Could not remove client.", LogLevel.Debug);
                                }
                            }
                            else if (clients[i].message != null && clients[i].message.IsCompleted)
                            {
                                switch (clients[i].message.Result.MessageTypeCase)
                                {
                                    case ConnectionMessage.MessageTypeOneofCase.ConnectionRequest:
                                        _currentWrites.Add(SendMessageAsync(clients[i].stream, new ConnectionMessage 
                                        { 
                                            ConnectionResonse = new ConnectionMessage.Types.ConnectionResponse() 
                                            { 
                                                Confirm = _canAcceptClients 
                                            } 
                                        }));
                                        break;

                                    case ConnectionMessage.MessageTypeOneofCase.ResourceOwnershipRequest:

                                        if (SimulationManager.SimulationObjects.TryGetValue(clients[i].message.Result.ResourceOwnershipRequest.ResourceName, out SimObject resource) && resource.State.Owner == null)
                                        {
                                            _currentWrites.Add(SendMessageAsync(clients[i].stream, new ConnectionMessage
                                            {
                                                ResourceOwnershipResponse = new ConnectionMessage.Types.ResourceOwnershipResponse()
                                                {
                                                    ResourceName = clients[i].message.Result.ResourceOwnershipRequest.ResourceName,
                                                    Confirm = true,
                                                    Guid = resource.State.Guid,
                                                    Generation = resource.State.Generation
                                                }
                                            }));
                                            resource.State.Owner = clients[i].client;
                                        }
                                        else
                                        {
                                            _currentWrites.Add(SendMessageAsync(clients[i].stream, new ConnectionMessage
                                            {
                                                ResourceOwnershipResponse = new ConnectionMessage.Types.ResourceOwnershipResponse()
                                                {
                                                    ResourceName = clients[i].message.Result.ResourceOwnershipRequest.ResourceName,
                                                    Confirm = false,
                                                    Error = "Resource could not be given"
                                                }
                                            }));
                                        }
                                        break;

                                    case ConnectionMessage.MessageTypeOneofCase.TerminateConnectionRequest:
                                        if (SimulationManager.SimulationObjects.TryGetValue(clients[i].message.Result.TerminateConnectionRequest.ResourceName, out SimObject tmp) && clients[i].message.Result.TerminateConnectionRequest.Guid.Equals(tmp.State.Guid) && clients[i].message.Result.TerminateConnectionRequest.Generation.Equals(tmp.State.Generation))
                                        {
                                            _currentWrites.Add(SendMessageAsync(clients[i].stream, new ConnectionMessage
                                            {
                                                TerminateConnectionResponse = new ConnectionMessage.Types.TerminateConnectionResponse()
                                                {
                                                    Confirm = true,
                                                    ResourceName = clients[i].message.Result.TerminateConnectionRequest.ResourceName
                                                }
                                            }));
                                            
                                            for (int j = clients[i].currentResources.Count - 1; j >= 0; j--)
                                            {
                                                if (clients[i].currentResources[j].Guid.Equals(clients[i].message.Result.TerminateConnectionRequest.Guid))
                                                {
                                                    clients[i].currentResources[j].ReleaseResource();
                                                    clients[i].currentResources.RemoveAt(j);
                                                }
                                            }
                                            
                                        }
                                        else
                                        {
                                            _currentWrites.Add(SendMessageAsync(clients[i].stream, new ConnectionMessage
                                            {
                                                TerminateConnectionResponse = new ConnectionMessage.Types.TerminateConnectionResponse()
                                                {
                                                    Confirm = false,
                                                    Error = "Cannot terminate connection from resource"
                                                }
                                            }));
                                        }
                                        break;

                                    case ConnectionMessage.MessageTypeOneofCase.Heartbeat:
                                        clients[i].state.LastHeartbeat = DateTimeOffset.Now.ToUnixTimeMilliseconds();
                                        break;

                                    default:
                                        System.Diagnostics.Debug.WriteLine("Invalid Message Recieved");
                                        break;
                                }
                                clients[i].message = null;
                            }
                            if (clients[i].message == null && clients[i].stream.DataAvailable)
                            {
                                clients[i].message = ParseMessageAsync(clients[i].stream);
                            }
                        }
                    }
                });
                */

                /*
                writerThread = new Thread(() =>
                {
                    while (IsRunning || _currentWrites.Count > 0)
                    {
                        for (int i = _currentWrites.Count - 1; i >= 0; i--)
                        {
                            if (_currentWrites[i] != null && _currentWrites[i].IsCompleted)
                            {
                                _currentWrites.RemoveAt(i);
                            }
                        }
                    }
                });
                */

                //listenerThread.Start();
                clientManagerThread.Start();
                writerThread.Start();

            }

            private async Task<ConnectionMessage> ParseMessageAsync(NetworkStream stream)
            {
                return await Task.Run(() => { return ConnectionMessage.Parser.ParseDelimitedFrom(stream); });
            }
            private async Task SendMessageAsync(NetworkStream stream, ConnectionMessage message)
            {
                await Task.Run(() => message.WriteDelimitedTo(stream));
            }

            private bool RemoveClient(ClientHandler clientHandler)
            {
                for (int i = clientHandler.currentResources.Count - 1; i >= 0; i--)
                {
                    clientHandler.currentResources[i].ReleaseResource();
                    clientHandler.currentResources.RemoveAt(i);
                }
                clientHandler.stream.Close();
                clientHandler.client.Close();
                return true;//clients.Remove(clientHandler);
            }

        }

        public static void Start()
        {
            if (Server.Instance.IsRunning) return;
            Server.Instance.IsRunning = true;
        }
        
        public static void Stop()
        {
            Server.Instance.IsRunning = false;
        }

        public static bool CanAcceptClients
        {
            get => Server.Instance._canAcceptClients;
            set => Server.Instance._canAcceptClients = value;
        }

        public static bool IsRunning { get => Server.Instance.IsRunning; }
    }
}