import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import api from '../lib/api';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Textarea } from '../components/ui/textarea';
import { Button } from '../components/ui/button';
import { ArrowLeft, Loader2, MapPin, Users, Pencil } from 'lucide-react';
import { toast } from '../components/ui/sonner';

export default function CircleDetail() {
  const { id } = useParams();
  const { user } = useAuth();
  const navigate = useNavigate();
  const [circle, setCircle] = useState(null);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState(false);
  const [form, setForm] = useState({});
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    api.get(`/circles/${id}/`).then(r => {
      setCircle(r.data);
      setForm({ name: r.data.name, description: r.data.description, address: r.data.address });
    }).catch(() => {}).finally(() => setLoading(false));
  }, [id]);

  const canEdit = circle && (
    user?.is_site_manager ||
    user?.admin_circle_ids?.includes(circle.id)
  );

  const handleSave = async () => {
    setSaving(true);
    try {
      const csrf = document.cookie.match(/csrftoken=([^;]+)/)?.[1];
      const r = await api.patch(`/circles/${id}/`, form);
      setCircle(r.data);
      setEditing(false);
      toast.success('Circle updated');
    } catch (e) { toast.error(e.response?.data?.error || 'Failed to save'); }
    finally { setSaving(false); }
  };

  if (loading) return <div className="flex justify-center py-16"><Loader2 className="h-5 w-5 animate-spin text-gray-400" /></div>;
  if (!circle) return <div className="empty-state"><p className="text-sm text-gray-500">Circle not found</p></div>;

  return (
    <div data-testid="circle-detail-page">
      <button onClick={() => navigate(-1)} className="flex items-center gap-1 text-xs text-gray-400 hover:text-black transition-colors mb-6" data-testid="back-btn">
        <ArrowLeft className="h-3.5 w-3.5" /> Back
      </button>

      {editing ? (
        <div className="max-w-lg space-y-4">
          <h1 className="section-title">Edit Circle</h1>
          <div>
            <Label className="text-xs font-medium uppercase tracking-wider text-gray-500">Name</Label>
            <Input value={form.name || ''} onChange={e => setForm(p => ({ ...p, name: e.target.value }))} className="mt-1 rounded-sm" data-testid="circle-edit-name" />
          </div>
          <div>
            <Label className="text-xs font-medium uppercase tracking-wider text-gray-500">Description</Label>
            <Textarea value={form.description || ''} onChange={e => setForm(p => ({ ...p, description: e.target.value }))} className="mt-1 rounded-sm" rows={4} data-testid="circle-edit-description" />
          </div>
          <div>
            <Label className="text-xs font-medium uppercase tracking-wider text-gray-500">Address</Label>
            <Input value={form.address || ''} onChange={e => setForm(p => ({ ...p, address: e.target.value }))} className="mt-1 rounded-sm" data-testid="circle-edit-address" />
          </div>
          <div className="flex gap-2">
            <Button onClick={handleSave} className="rounded-sm bg-black text-white hover:bg-gray-800" disabled={saving} data-testid="circle-edit-save">
              {saving ? <Loader2 className="h-4 w-4 animate-spin" /> : 'Save'}
            </Button>
            <Button variant="outline" className="rounded-sm" onClick={() => setEditing(false)} data-testid="circle-edit-cancel">Cancel</Button>
          </div>
        </div>
      ) : (
        <div>
          <div className="flex items-start justify-between">
            <div>
              <h1 className="text-2xl sm:text-3xl font-medium tracking-tight text-black" style={{ fontFamily: 'Outfit' }} data-testid="circle-name">{circle.name}</h1>
              <p className="text-xs text-gray-400 mt-1">/{circle.slug}</p>
            </div>
            {canEdit && (
              <Button variant="outline" size="sm" className="rounded-sm text-xs gap-1" onClick={() => setEditing(true)} data-testid="circle-edit-btn">
                <Pencil className="h-3.5 w-3.5" /> Edit
              </Button>
            )}
          </div>

          {circle.address && (
            <div className="flex items-center gap-1.5 mt-4 text-sm text-gray-500">
              <MapPin className="h-4 w-4" /> {circle.address}
            </div>
          )}

          {circle.description && (
            <div className="mt-4 text-sm text-gray-700 leading-relaxed whitespace-pre-wrap" data-testid="circle-description">
              {circle.description}
            </div>
          )}

          <div className="mt-6 flex items-center gap-1.5 text-sm text-gray-400">
            <Users className="h-4 w-4" /> {circle.members_count ?? '—'} members
          </div>
        </div>
      )}
    </div>
  );
}
