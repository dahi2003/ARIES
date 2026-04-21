export function saveAuth(token: string, role: string) {
  localStorage.setItem('access_token', token);
  localStorage.setItem('user_role', role);
}

export function getStoredRole(): string | null {
  return localStorage.getItem('user_role');
}

export function logout() {
  localStorage.removeItem('access_token');
  localStorage.removeItem('user_role');
}
