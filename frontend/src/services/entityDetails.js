import { callEntityApi } from "./entities.js";

export function getEntityDetail(entityKey, name, signal) {
  return callEntityApi("get_entity_detail", { entity_key: entityKey, name }, signal);
}
