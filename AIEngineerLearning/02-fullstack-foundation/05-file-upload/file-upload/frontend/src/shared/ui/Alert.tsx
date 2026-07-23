import type {
  PropsWithChildren,
} from "react";


interface AlertProps {
  variant: "error" | "success";
}


export function Alert({
  variant,
  children,
}: PropsWithChildren<AlertProps>) {
  return (
    <div
      className={`alert alert-${variant}`}
      role={
        variant === "error"
          ? "alert"
          : "status"
      }
    >
      {children}
    </div>
  );
}