import { Button } from '../components/ui/button';
import { ChevronLeft, ChevronRight } from 'lucide-react';

export default function Pagination({ pagination, onPageChange }) {
  if (!pagination || pagination.total_pages <= 1) return null;
  const { page, total_pages, total } = pagination;
  return (
    <div className="flex items-center justify-between pt-4 mt-4 border-t border-gray-100" data-testid="pagination">
      <span className="text-xs text-gray-400">{total} total</span>
      <div className="flex items-center gap-1">
        <Button variant="ghost" size="sm" className="h-7 w-7 p-0" disabled={page <= 1} onClick={() => onPageChange(page - 1)} data-testid="pagination-prev" aria-label="Previous page">
          <ChevronLeft className="h-3.5 w-3.5" />
        </Button>
        <span className="text-xs text-gray-600 px-2">{page} / {total_pages}</span>
        <Button variant="ghost" size="sm" className="h-7 w-7 p-0" disabled={page >= total_pages} onClick={() => onPageChange(page + 1)} data-testid="pagination-next" aria-label="Next page">
          <ChevronRight className="h-3.5 w-3.5" />
        </Button>
      </div>
    </div>
  );
}
