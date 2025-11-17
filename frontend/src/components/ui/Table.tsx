import React from 'react';

export interface Column<T> {
  key: string;
  header: string;
  render?: (item: T) => React.ReactNode;
  width?: string;
}

export interface TableProps<T> {
  data: T[];
  columns: Column<T>[];
  keyExtractor: (item: T) => string;
  emptyMessage?: string;
  className?: string;
}

function Table<T>({
  data,
  columns,
  keyExtractor,
  emptyMessage = 'No data available',
  className = '',
}: TableProps<T>) {
  if (data.length === 0) {
    return (
      <div className="text-center py-12 text-slate-500 dark:text-slate-400">
        <p>{emptyMessage}</p>
      </div>
    );
  }

  return (
    <div className={`overflow-x-auto ${className}`}>
      <table className="w-full">
        <thead className="bg-slate-50 dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800">
          <tr>
            {columns.map((column) => (
              <th
                key={column.key}
                className="px-6 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider"
                style={{ width: column.width }}
              >
                {column.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="bg-white dark:bg-slate-950 divide-y divide-slate-200 dark:divide-slate-800">
          {data.map((item) => (
            <tr
              key={keyExtractor(item)}
              className="hover:bg-slate-50 dark:hover:bg-slate-900/50 transition-colors"
            >
              {columns.map((column) => (
                <td
                  key={column.key}
                  className="px-6 py-4 whitespace-nowrap text-sm text-slate-900 dark:text-slate-100"
                >
                  {column.render
                    ? column.render(item)
                    : (item as any)[column.key]}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default Table;
