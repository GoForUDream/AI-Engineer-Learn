import { Link } from "react-router-dom";

export function NotFoundPage() {
  return (
    <main className="page-container">
      <section className="panel empty-state">
        <h1>Page not found</h1>

        <p>
          The page you requested does not
          exist.
        </p>

        <Link to="/todos">
          Return to todos
        </Link>
      </section>
    </main>
  );
}