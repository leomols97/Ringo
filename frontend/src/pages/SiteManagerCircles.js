import { useState, useEffect, useCallback } from 'react';
import api from '../lib/api';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Textarea } from '../components/ui/textarea';
import {
  Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter, DialogTrigger,
} from '../components/ui/dialog';
import {
  AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent,
  AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle, AlertDialogTrigger,
} from '../components/ui/alert-dialog';
import { Loader2, Plus, Pencil, Trash2, CircleDot } from 'lucide-react';

const emptyForm = { name: '', slug: '', description: '' };

export default function SiteManagerCircles() {
  const [circles, setCircles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [form, setForm] = useState(emptyForm);
  const [editId, setEditId] = useState(null);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  const fetchCircles = useCallback(async () => {
    setLoading(true);
    try {
      const r = await api.get('/circles/');
      setCircles(r.data.circles || []);
    } catch { setCircles([]); }
    finally { setLoading(false); }
  }, []);

  useEffect(() => { fetchCircles(); }, [fetchCircles]);

  const openCreate = () => { setForm(emptyForm); setEditId(null); setError(''); setDialogOpen(true); };
  const openEdit = (c) => {
    setForm({ name: c.name, slug: c.slug, description: c.description || '' });
    setEditId(c.id);
    setError('');
    setDialogOpen(true);
  };

  const handleSave = async () => {
    setSaving(true); setError('');
    try {
      if (editId) {
        await api.patch(`/circles/${editId}/`, { name: form.name, description: form.description });
      } else {
        await api.post('/circles/', form);
      }
      setDialogOpen(false);
      fetchCircles();
    } catch (e) {
      setError(e.response?.data?.error || 'Failed to save');
    } finally { setSaving(false); }
  };

  const handleDelete = async (cid) => {
    await api.delete(`/circles/${cid}/`);
    fetchCircles();
  };

  const update = (k, v) => setForm(p => ({ ...p, [k]: v }));

  return (
    <div data-testid="site-manager-circles-page">
      <div className="flex items-center justify-between">
        <h1 className="section-title">All Circles</h1>
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger asChild>
            <Button onClick={openCreate} className="rounded-sm bg-black text-white hover:bg-gray-800 gap-1" data-testid="create-circle-btn">
              <Plus className="h-4 w-4" /> New circle
            </Button>
          </DialogTrigger>
          <DialogContent className="rounded-sm max-w-md">
            <DialogHeader><DialogTitle style={{ fontFamily: 'Outfit' }}>{editId ? 'Edit circle' : 'New circle'}</DialogTitle></DialogHeader>
            {error && <div className="p-3 text-sm text-red-600 border border-red-200 rounded-sm bg-red-50">{error}</div>}
            <div className="space-y-3 py-2">
              <div>
                <Label className="text-xs uppercase tracking-wider text-gray-500">Name</Label>
                <Input value={form.name} onChange={e => update('name', e.target.value)} className="mt-1 rounded-sm" data-testid="circle-form-name" />
              </div>
              {!editId && (
                <div>
                  <Label className="text-xs uppercase tracking-wider text-gray-500">Slug</Label>
                  <Input value={form.slug} onChange={e => update('slug', e.target.value.toLowerCase().replace(/[^a-z0-9-]/g, '-'))} className="mt-1 rounded-sm" data-testid="circle-form-slug" placeholder="unique-url-slug" />
                </div>
              )}
              <div>
                <Label className="text-xs uppercase tracking-wider text-gray-500">Description</Label>
                <Textarea value={form.description} onChange={e => update('description', e.target.value)} className="mt-1 rounded-sm" rows={3} data-testid="circle-form-desc" />
              </div>
            </div>
            <DialogFooter>
              <Button onClick={handleSave} className="rounded-sm bg-black text-white hover:bg-gray-800" disabled={saving} data-testid="circle-form-save">
                {saving ? <Loader2 className="h-4 w-4 animate-spin" /> : editId ? 'Update' : 'Create'}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      {loading ? (
        <div className="flex justify-center py-12"><Loader2 className="h-5 w-5 animate-spin text-gray-400" /></div>
      ) : circles.length === 0 ? (
        <div className="empty-state"><CircleDot className="h-8 w-8 text-gray-300" /><p className="empty-state-text mt-3">No circles created yet</p></div>
      ) : (
        <div className="mt-6 border-t border-gray-200">
          {circles.map(c => (
            <div key={c.id} className="data-row px-1" data-testid={`circle-row-${c.id}`}>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-black">{c.name}</p>
                <div className="flex items-center gap-3 mt-0.5 text-xs text-gray-400">
                  <span>/{c.slug}</span>
                  <span>{c.members_count || 0} members</span>
                </div>
              </div>
              <div className="flex items-center gap-1 shrink-0">
                <Button variant="ghost" size="sm" className="h-7 w-7 p-0" onClick={() => openEdit(c)} data-testid={`edit-circle-${c.id}`}>
                  <Pencil className="h-3.5 w-3.5" />
                </Button>
                <AlertDialog>
                  <AlertDialogTrigger asChild>
                    <Button variant="ghost" size="sm" className="h-7 w-7 p-0 text-red-600" data-testid={`delete-trigger-${c.id}`}><Trash2 className="h-3.5 w-3.5" /></Button>
                  </AlertDialogTrigger>
                  <AlertDialogContent className="rounded-sm">
                    <AlertDialogHeader>
                      <AlertDialogTitle>Delete circle?</AlertDialogTitle>
                      <AlertDialogDescription>Delete "{c.name}" and all its data? This cannot be undone.</AlertDialogDescription>
                    </AlertDialogHeader>
                    <AlertDialogFooter>
                      <AlertDialogCancel className="rounded-sm">Cancel</AlertDialogCancel>
                      <AlertDialogAction onClick={() => handleDelete(c.id)} className="rounded-sm bg-red-600 hover:bg-red-700" data-testid={`delete-confirm-${c.id}`}>Delete</AlertDialogAction>
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
