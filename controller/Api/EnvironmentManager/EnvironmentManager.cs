﻿using System;
using System.Collections.Generic;
using System.Linq;
using SynthesisAPI.Modules;
using UnityEngine.PlayerLoop;

//Entity is a 32 bit generational index
// 1st 16 bits represent index
// 2nd 16 bits represent generation
using Entity = System.UInt32;

namespace SynthesisAPI.EnvironmentManager
{
    /// <summary>
    /// ECS System
    /// </summary>
    public static class EnvironmentManager
    {
        static AnyMap components = new AnyMap(); //dynamic mapping of components to Entity by index
        static List<Entity> entities = new List<Entity>(); //Entities that are in environment 
        static Stack<Entity> removed = new Stack<Entity>(); //deallocated Entities that still exist in entities null Entities

        const Entity NULL_ENTITY = 0;
        const ushort BASE_GEN = 1; //no entity should have a generation of 0


        #region EntityManagement

        /// <summary>
        /// Create and allocate new entity
        /// </summary>
        /// <returns>new Entity</returns>
        public static Entity AddEntity()
        {
            Entity newEntity;
            if (removed.Count > 0) //allocates empty/deallocated spaces in entities
            {
                Entity oldEntity = removed.Pop();
                ushort oldEntityIndex = oldEntity.GetIndex();
                ushort oldEntityGen = oldEntity.GetGen();
                newEntity = oldEntity.SetGen((ushort)(oldEntityGen + 1));
                entities[oldEntityIndex] = newEntity;
            }
            else //adds entity by increasing entity list size
            {
                newEntity = CreateEntity((ushort)entities.Count, BASE_GEN);
                entities.Add(newEntity);
            }
            return newEntity;
        }

        /// <summary>
        /// Remove and deallocate entity
        /// </summary>
        /// <param name="entity">entity to be removed</param>
        /// <returns>if entity was removed - will only return false if entity does not exist/is not allocated</returns>
        public static bool RemoveEntity(this Entity entity)
        {
            if (!EntityExists(entity))
                return false;
            removed.Push(entity); //deallocate entity
            entities[entity.GetIndex()] = NULL_ENTITY; //invalidate components
            return true;
        }

        /// <summary>
        /// Check if entity exists in current context
        /// </summary>
        /// <param name="entity">entity to be checked</param>
        /// <returns>if entity equals the entity in its given index</returns>
        public static bool EntityExists(this Entity entity)
        {
            ushort entityIndex = entity.GetIndex();
            return entityIndex < entities.Count && entities[entityIndex] == entity;
        }

        #endregion

        #region ComponentManagement

        /// <summary>
        /// Get component of type, TComponent, that is associated with the given entity
        /// </summary>
        /// <typeparam name="TComponent">Component type</typeparam>
        /// <param name="entity">given entity</param>
        /// <returns>Component instance</returns>
        public static TComponent? GetComponent<TComponent>(this Entity entity) where TComponent : Component
        {
            return (TComponent?) GetComponent(entity, typeof(TComponent));
        }

        public static Component? GetComponent(this Entity entity,Type componentType)
        {
            if (IsComponent(componentType) && EntityExists(entity))
                return components.Get(entity,componentType);
            return null;
        }

        /// <summary>
        /// Set component of type, TComponent, to the given entity
        /// </summary>
        /// <typeparam name="T">Component Type</typeparam>
        /// <param name="entity">given entity</param>
        /// <param name="component">instance of component to be set</param>
        public static void SetComponent(this Entity entity, Component component)
        {
            if (EntityExists(entity))
                components.Set(entity, component);
        }

        /// <summary>
        /// Remove component (sets component to null) of type, TComponent, from given entity
        /// </summary>
        /// <typeparam name="TComponent">Component Type</typeparam>
        /// <param name="entity">given entity</param>
        public static void RemoveComponent<TComponent>(this Entity entity) where TComponent : Component
        {
            RemoveComponent(entity, typeof(TComponent));
        }

        public static void RemoveComponent(this Entity entity, Type componentType)
        {
            if (IsComponent(componentType) && EntityExists(entity))
                components.Remove(entity, componentType);

        }

        private static bool IsComponent(Type type)
        {
            return type.IsSubclassOf(typeof(Component)) || type == typeof(Component);
        }

        #endregion

        #region EntityBitModifier

        private static ushort GetIndex(this Entity entity)
        {
            return (ushort)(entity >> 16);
        }
        //last 16 bits
        private static ushort GetGen(this Entity entity)
        {
            return (ushort)(entity & 65535);
        }
        private static Entity CreateEntity(ushort index, ushort gen)
        {
            return ((uint)index << 16) + gen;
        }
        private static Entity SetIndex(this Entity entity, ushort index)
        {
            return ((uint)index << 16) + (entity & 65535);
        }
        private static Entity SetGen(this Entity entity, ushort gen)
        {
            return (entity & 4294901760) + gen;
        }

        public static void Clear()
        {
            if (AppDomain.CurrentDomain.GetAssemblies()
                .Any(a => a.FullName.ToLowerInvariant().StartsWith("nunit.framework")))
            {
                components.Clear();
                entities.Clear();
                removed.Clear();
            }
            else
            {
                throw new Exception("Users are not allowed to clear the environment manager");
            }
        }

        #endregion

        #region AnyMap

        /// <summary>
        /// Dynamic mapping of any reference type to its corresponding GenIndexArray
        /// </summary>
        class AnyMap
        {
            Dictionary<Type, GenIndexArray> componentDict; 
            public AnyMap()
            {
                componentDict = new Dictionary<Type, GenIndexArray>();
            }
            public void Set(Entity entity, Component val)
            {
                if (componentDict.TryGetValue(val.GetType(), out GenIndexArray arr))
                    arr.Set(entity, val);
                else
                {
                    componentDict.Add(val.GetType(), new GenIndexArray());
                    Set(entity, val);
                }
            }

            public void Remove(Entity entity,Type componentType)
            {
                if (componentDict.TryGetValue(componentType, out GenIndexArray arr))
                    arr.Set(entity, null);
            }

            public Component? Get(Entity entity,Type componentType)
            {
                if (componentDict.TryGetValue(componentType, out GenIndexArray arr))
                {
                    return arr.Get(entity);
                }
                else
                    return null;
            }

            public void Clear()
            {
                componentDict.Clear();
            }

            #region GenIndexArray

            /// <summary>
            /// Maps Entity to its component by its index : component index in entries is the same as Entity index
            /// </summary>
            class GenIndexArray
            {
                List<Entry> entries;

                public GenIndexArray()
                {
                    entries = new List<Entry>();
                }

                struct Entry
                {
                    public Entry(Component? val, ulong gen)
                    {
                        Val = val;
                        Gen = gen;
                    }
                    public Component? Val { get; }
                    public ulong Gen { get; }
                }

                public void Set(Entity entity, Component? val)
                {
                    ushort entityIndex = entity.GetIndex();
                    ushort entityGen = entity.GetGen();
                    if (entityIndex < entries.Count)
                        entries[entityIndex] = new Entry(val, entityGen);
                    else
                    {
                        //increase list size by populating "null" Entry so we can add value at index which is outside of bounds
                        for (int i = entries.Count; i < entityIndex; i++)
                            entries.Add(new Entry(null, 0)); //no Entity has gen of 0 so these entries can never be accessed
                        entries.Add(new Entry(val, entityGen));
                    }
                }

                public Component? Get(Entity entity)
                {
                    ushort entityIndex = entity.GetIndex();
                    ushort entityGen = entity.GetGen();
                    if (entityIndex >= entries.Count)
                        return null; //prevents IndexOutOfBoundsException
                    Entry entry = entries[entityIndex];
                    //only get component if generations match - avoids having reallocated Entities point to the components of deallocated Entities
                    if (entry.Gen == entityGen)
                        return entry.Val;
                    return null;
                }
            }

            #endregion
        }

        #endregion
    }
}