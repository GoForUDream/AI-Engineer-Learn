import type {
  TodoFilterValue,
} from "../types";

interface TodoFilterProps {
  value: TodoFilterValue;
  onChange: (
    value: TodoFilterValue,
  ) => void;
}

const FILTER_OPTIONS: ReadonlyArray<{
  value: TodoFilterValue;
  label: string;
}> = [
  {
    value: "all",
    label: "All",
  },
  {
    value: "active",
    label: "Active",
  },
  {
    value: "completed",
    label: "Completed",
  },
];

export function TodoFilter({
  value,
  onChange,
}: TodoFilterProps) {
  return (
    <fieldset className="todo-filter">
      <legend>Filter todos</legend>

      <div className="filter-options">
        {FILTER_OPTIONS.map((option) => (
          <label key={option.value}>
            <input
              type="radio"
              name="todo-filter"
              value={option.value}
              checked={value === option.value}
              onChange={() => {
                onChange(option.value);
              }}
            />

            <span>{option.label}</span>
          </label>
        ))}
      </div>
    </fieldset>
  );
}