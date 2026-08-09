'use client';
import { useState, useEffect, useCallback } from 'react';
import { api } from '@/lib/api';
import type { RunDetail } from '@/types/run';

export function useRun(runId: string, pollInterval = 2000) {
  const [run, setRun] = useState<RunDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetch = useCallback(async () => {
    if (!runId) return;
    try {
      const data = await api.runs.get(runId);
      setRun(data);
      setError(null);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setLoading(false);
    }
  }, [runId]);

  useEffect(() => {
    fetch();
    // Stop polling when terminal
    const interval = setInterval(() => {
      if (run?.status === 'COMPLETED' || run?.status === 'TERMINATED' || run?.status === 'FAILED') {
        return;
      }
      fetch();
    }, pollInterval);
    return () => clearInterval(interval);
  }, [fetch, pollInterval, run?.status]);

  return { run, loading, error, refresh: fetch };
}
