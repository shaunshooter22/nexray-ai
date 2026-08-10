import { ChevronRight } from "lucide-react";
import { Link } from "react-router-dom";
import { Fragment } from "react";

interface Crumb {
  label: string;
  to?: string;
}

export function Breadcrumb({ items }: { items: Crumb[] }) {
  return (
    <nav aria-label="Breadcrumb" className="flex items-center gap-1.5 text-body-sm">
      {items.map((item, i) => (
        <Fragment key={item.label}>
          {i > 0 && <ChevronRight size={14} className="text-text-disabled" />}
          {item.to ? (
            <Link to={item.to} className="text-text-secondary hover:text-primary">
              {item.label}
            </Link>
          ) : (
            <span className="text-text-primary font-medium">{item.label}</span>
          )}
        </Fragment>
      ))}
    </nav>
  );
}
