import { useState, useEffect, useCallback } from 'react';
import { useApp } from '../contexts/AppContext';
import { useAuth } from '../contexts/AuthContext';
import { Link } from 'react-router-dom';
import api from '../lib/api';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Textarea } from '../components/ui/textarea';
import { Switch } from '../components/ui/switch';
import {
  Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter, DialogTrigger,
} from '../components/ui/dialog';
import {
  AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent,
  AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle, AlertDialogTrigger,
} from '../components/ui/alert-dialog';
import { Loader2, Plus, Pencil, Trash2, Users, Calendar } from 'lucide-react';

const emptyForm = { title: '', description: '', location: '', start_datetime: '', end_datetime: '', published: true };

export default function AdminEvents() {
  const { user } = useAuth();
  const { activeCircle, adminCircles } = useApp();
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [form, setForm] = useState(emptyForm);
  const [editId, setEditId] = useState(null);
  const [saving, setSaving] = useState(false);
  const [pubFilter, setPubFilter] = useState('all');

  const circle = activeCircle && (user?.is_site_manager || adminCircles.find(c => c.id === activeCircle.id))
    ? activeCircle
    : adminCircles[0] || null;

  const fetchEvents = useCallback(async () => {
    if (!circle) return;
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (pubFilter !== 'all') params.set('published', pubFilter);
      const r = await api.get(`/circles/${circle.id}/events/?${params}`);
      setEvents(r.data.events || []);
    } catch { setEvents([]); }
    finally { setLoading(false); }
  }, [circle, pubFilter]);

  useEffect(() => { fetchEvents(); }, [fetchEvents]);

  const openCreate = () => { setForm(emptyForm); setEditId(null); setDialogOpen(true); };
  const openEdit = (ev) => {
    setForm({
      title: ev.title, description: ev.description || '', location: ev.location || '',
      start_datetime: ev.start_datetime?.slice(0, 16) || '', end_datetime: ev.end_datetime?.slice(0, 16) || '',
      published: ev.published,
    });
    setEditId(ev.id);
    setDialogOpen(true);
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      const payload = { ...form };
      if (payload.start_datetime && !payload.start_datetime.includes('T')) payload.start_datetime += 'T00:00';
      if (payload.end_datetime && !payload.end_datetime.includes('T')) payload.end_datetime += 'T00:00';
      if (editId) {
        await api.patch(`/events/${editId}/`, payload);
      } else {
        await api.post(`/circles/${circle.id}/events/`, payload);
      }
      setDialogOpen(false);
      fetchEvents();
    } catch {}
    finally { setSaving(false); }
  };

  const handleDelete = async (eid) => {
    await api.delete(`/events/${eid}/`);
    fetchEvents();
  };

  const update = (k, v) => setForm(p => ({ ...p, [k]: v }));

  if (!circle) return <div className="empty-state"><Calendar className="h-10 w-10 text-gray-300" /><p className="empty-state-text mt-3">Select an admin circle.</p></div>;

  return (
    <div data-testid="admin-events-page">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-xs uppercase tracking-[0.2em] font-bold text-gray-400">{circle.name}</p>
          <h1 className="section-title mt-1">Events</h1>
        </div>
        <div className="flex items-center gap-2">
          <select value={pubFilter} onChange={e => setPubFilter(e.target.value)} className="text-xs border border-gray-200 rounded-sm px-2 h-8 bg-white" data-testid="events-filter" aria-label="Filter events">
            <option value="all">All</option>
            <option value="true">Published</option>
            <option value="false">Drafts</option>
          </select>
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger asChild>
            <Button onClick={openCreate} className="rounded-sm bg-black text-white hover:bg-gray-800 gap-1" data-testid="create-event-btn">
              <Plus className="h-4 w-4" /> New event
            </Button>
          </DialogTrigger>
          <DialogContent className="rounded-sm max-w-md">
            <DialogHeader><DialogTitle style={{ fontFamily: 'Outfit' }}>{editId ? 'Edit event' : 'New event'}</DialogTitle></DialogHeader>
            <div className="space-y-3 py-2">
              <div>
                <Label className="text-xs uppercase tracking-wider text-gray-500">Title</Label>
                <Input value={form.title} onChange={e => update('title', e.target.value)} className="mt-1 rounded-sm" data-testid="event-form-title" />
              </div>
              <div>
                <Label className="text-xs uppercase tracking-wider text-gray-500">Description</Label>
                <Textarea value={form.description} onChange={e => update('description', e.target.value)} className="mt-1 rounded-sm" rows={3} data-testid="event-form-desc" />
              </div>
              <div>
                <Label className="text-xs uppercase tracking-wider text-gray-500">Location</Label>
                <Input value={form.location} onChange={e => update('location', e.target.value)} className="mt-1 rounded-sm" data-testid="event-form-location" />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <Label className="text-xs uppercase tracking-wider text-gray-500">Start</Label>
                  <Input type="datetime-local" value={form.start_datetime} onChange={e => update('start_datetime', e.target.value)} className="mt-1 rounded-sm text-xs" data-testid="event-form-start" />
                </div>
                <div>
                  <Label className="text-xs uppercase tracking-wider text-gray-500">End</Label>
                  <Input type="datetime-local" value={form.end_datetime} onChange={e => update('end_datetime', e.target.value)} className="mt-1 rounded-sm text-xs" data-testid="event-form-end" />
                </div>
              </div>
              <div className="flex items-center gap-2">
                <Switch checked={form.published} onCheckedChange={v => update('published', v)} data-testid="event-form-published" />
                <Label className="text-xs text-gray-500">Published</Label>
              </div>
            </div>
            <DialogFooter>
              <Button onClick={handleSave} className="rounded-sm bg-black text-white hover:bg-gray-800" disabled={saving} data-testid="event-form-save">
                {saving ? <Loader2 className="h-4 w-4 animate-spin" /> : editId ? 'Update' : 'Create'}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
        </div>
      </div>

      {loading ? (
        <div className="flex justify-center py-12"><Loader2 className="h-5 w-5 animate-spin text-gray-400" /></div>
      ) : events.length === 0 ? (
        <div className="empty-state"><Calendar className="h-8 w-8 text-gray-300" /><p className="empty-state-text mt-3">No events yet</p></div>
      ) : (
        <div className="mt-6 border-t border-gray-200">
          {events.map(ev => (
            <div key={ev.id} className="data-row px-1" data-testid={`event-row-${ev.id}`}>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-black">{ev.title}</p>
                <p className="text-xs text-gray-400 mt-0.5">
                  {new Date(ev.start_datetime).toLocaleDateString()} {!ev.published && '(Draft)'}
                </p>
              </div>
              <div className="flex items-center gap-1 shrink-0">
                <Button variant="ghost" size="sm" className="h-7 w-7 p-0" asChild data-testid={`view-signups-${ev.id}`}>
                  <Link to={`/admin/events/${ev.id}/signups`}><Users className="h-3.5 w-3.5" /></Link>
                </Button>
                <Button variant="ghost" size="sm" className="h-7 w-7 p-0" onClick={() => openEdit(ev)} data-testid={`edit-event-${ev.id}`}>
                  <Pencil className="h-3.5 w-3.5" />
                </Button>
                <AlertDialog>
                  <AlertDialogTrigger asChild>
                    <Button variant="ghost" size="sm" className="h-7 w-7 p-0 text-red-600" data-testid={`delete-trigger-${ev.id}`}><Trash2 className="h-3.5 w-3.5" /></Button>
                  </AlertDialogTrigger>
                  <AlertDialogContent className="rounded-sm">
                    <AlertDialogHeader>
                      <AlertDialogTitle>Delete event?</AlertDialogTitle>
                      <AlertDialogDescription>Delete "{ev.title}"? This cannot be undone.</AlertDialogDescription>
                    </AlertDialogHeader>
                    <AlertDialogFooter>
                      <AlertDialogCancel className="rounded-sm">Cancel</AlertDialogCancel>
                      <AlertDialogAction onClick={() => handleDelete(ev.id)} className="rounded-sm bg-red-600 hover:bg-red-700" data-testid={`delete-confirm-${ev.id}`}>Delete</AlertDialogAction>
                    </AlertDialogFooter>
                  </AlertDialogContent>
                </AlertDialog>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
