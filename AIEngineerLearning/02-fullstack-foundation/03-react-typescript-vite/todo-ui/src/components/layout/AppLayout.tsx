import {
  NavLink,
  Outlet,
} from "react-router-dom";

export function AppLayout() {
  return (
    <div className="app-shell">
      <header className="app-navigation">
        <NavLink
          to="/todos"
          className="brand"
        >
          Todo UI
        </NavLink>

        <nav aria-label="Main navigation">
          <NavLink
            to="/todos"
            className={({ isActive }) =>
              isActive
                ? "nav-link active"
                : "nav-link"
            }
          >
            Todos
          </NavLink>

          <NavLink
            to="/settings"
            className={({ isActive }) =>
              isActive
                ? "nav-link active"
                : "nav-link"
            }
          >
            Settings
          </NavLink>
        </nav>
      </header>

      <Outlet />
    </div>
  );
}