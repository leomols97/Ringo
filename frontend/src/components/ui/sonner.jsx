import { Toaster as Sonner, toast } from "sonner"

const Toaster = ({ ...props }) => {
  return (
    <Sonner
      theme="light"
      className="toaster group"
      position="bottom-right"
      toastOptions={{
        classNames: {
          toast:
            "group toast group-[.toaster]:bg-white group-[.toaster]:text-black group-[.toaster]:border-gray-200 group-[.toaster]:shadow-none group-[.toaster]:border group-[.toaster]:rounded-sm group-[.toaster]:text-sm",
          description: "group-[.toast]:text-gray-500",
        },
      }}
      {...props} />
  );
}

export { Toaster, toast }
