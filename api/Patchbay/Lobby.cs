﻿using System;
using System.Collections.Generic;
using System.Net;
using System.Text;
using System.Threading;
using SynthesisServer.Proto;

using PLobby = SynthesisServer.Proto.Lobby;

namespace SynthesisServer {
    public class Lobby {
        // TODO: CATCH INDEX OUT OF BOUNDS
        //public string? Password { get; set; }
        public ClientData Host { get; private set; }
        public List<ClientData> Clients { get { return _clients; } }
        public string Name { get; private set; }
        public int LobbySize { get; set; }
        public bool IsStarted { get; private set; }

        private readonly List<ClientData> _clients;

        public Lobby(ClientData host, int lobbySize, string name) {
            IsStarted = false;
            _clients = new List<ClientData>();
            _clients.Add(host);
            Host = host;
            Name = name;
        }

        public void Start() {
            IsStarted = true;
        }

        public bool Swap(int firstIndex, int secondIndex) {
            try {
                if (IsStarted) {
                    return false;
                }
                var x = _clients[firstIndex];
                _clients[firstIndex] = _clients[secondIndex];
                _clients[secondIndex] = x;
                return true;
            } catch (IndexOutOfRangeException) {
                return false;
            }
        }

        public bool TryAddClient(ClientData client) {
            // If no index is specified, it will try to add the client to an empty index so long as it does not already have a spot

            if (IsStarted || _clients.Count >= LobbySize || _clients.Contains(client)) {
                return false;
            }
            if (_clients.Count == 0) {
                Host = client;
            }
            _clients.Add(client);
            return true;
        }

        public bool TryRemoveClient(ClientData client) {
            if (IsStarted) {
                return false;
            }
            if (client.Equals(Host)) {
                TryFindNewHost();
            }
            if (_clients.Contains(client)) {
                _clients.Remove(client);
            }
            return false;
        }

        private bool TryFindNewHost() {
            foreach (ClientData x in _clients) {
                if (x != null && !x.Equals(Host)) {
                    Host = x;
                    return true;
                }
            }
            return false;
        }

        public PLobby ToProtobuf() {
            var l = new PLobby();
            l.LobbyName = Name;
            Clients.ForEach(c => {
                l.Clients.Add(c.ID, c);
            });
            return l;
        }


    }
}