export function canCreate(permissions) {
  return Boolean(permissions?.can_create);
}

export function canRead(permissions) {
  return Boolean(permissions?.can_read);
}
