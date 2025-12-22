"use client";

import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { useStore } from "@/store";
import { deleteDataModel } from "@/store/slices/dialog-slice";
import { handleDelete } from "@/utils/handle-status-update-and-delete";
import { toast } from "sonner";

export function DeletionDialog() {
  const { isToggled, toggleDialog } = useStore((state) => state.dialog);
  const dialog = useStore((state) => state.dialog);
  const deleteData: deleteDataModel | undefined = dialog.deleteData;
  const { deleteTVListItem, deleteMovieListItem } = useStore(
    (state) => state.watchlists
  );

  return (
    <Dialog open={isToggled} onOpenChange={toggleDialog}>
      <DialogContent className="sm:max-w-[425px]">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            if (deleteData) {
              // FRONTEND
              if (deleteData.type === "tv") {
                deleteTVListItem(deleteData.item.imdb);
              } else {
                deleteMovieListItem(deleteData.item.imdb);
              }

              // BACKEND
              handleDelete(deleteData);
            } else {
              toast.error("No item selected for deletion.");
            }
            toggleDialog();
          }}>
          <DialogHeader>
            <DialogTitle>Are you sure?</DialogTitle>
          </DialogHeader>
          <DialogFooter>
            <Button type="submit" className="cursor-pointer">
              Yes, Delete
            </Button>
            <DialogClose asChild>
              <Button variant="outline" className="cursor-pointer">
                No
              </Button>
            </DialogClose>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
