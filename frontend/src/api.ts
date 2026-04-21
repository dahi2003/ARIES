const API_BASE = import.meta.env.VITE_API_BASE || '/api';

async function parseResponse(res: Response) {
  const text = await res.text();
  try {
    return JSON.parse(text);
  } catch {
    return { status: res.status, ok: res.ok, text };
  }
}

export async function apiPost(path: string, data: any, contentType = 'application/json') {
  const token = localStorage.getItem('access_token');
  const headers: Record<string, string> = {
    Authorization: token ? `Bearer ${token}` : '',
  };
  if (contentType) {
    headers['Content-Type'] = contentType;
  }
  const res = await fetch(`${API_BASE}${path}`, {
    method: 'POST',
    headers,
    body: typeof data === 'string' ? data : JSON.stringify(data),
  });
  return parseResponse(res);
}

export async function apiPostForm(path: string, formData: FormData) {
  const token = localStorage.getItem('access_token');
  const headers: Record<string, string> = {
    Authorization: token ? `Bearer ${token}` : '',
  };

  const res = await fetch(`${API_BASE}${path}`, {
    method: 'POST',
    headers,
    body: formData,
  });

  const text = await res.text();
  try {
    return JSON.parse(text);
  } catch {
    return { status: res.status, ok: res.ok, text };
  }
}

export async function apiGet(path: string) {
  const token = localStorage.getItem('access_token');
  const res = await fetch(`${API_BASE}${path}`, {
    headers: {
      Authorization: token ? `Bearer ${token}` : '',
    },
  });
  return parseResponse(res);
}
