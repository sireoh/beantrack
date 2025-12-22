"use client";

import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { handleStatusUpdateAndDelete } from "@/utils/handle-status-update-and-delete";
import {
  TvMinimalPlay,
  SquareCheckBig,
  NotebookPen,
  OctagonPause,
  BookmarkX,
  Trash2,
} from "lucide-react";
import { Fragment } from "react";
import { ItemCardDataModel } from "./item-card";
import { useStore } from "@/store";
import { deleteDataModel } from "@/store/slices/dialog-slice";

const ItemCardEditButtonDropdown = ({
  item,
  type,
}: {
  item: ItemCardDataModel;
  type: string;
}) => {
  const { toggleDialog, setDeleteData } = useStore((state) => state.dialog);

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="outline" className="cursor-pointer">
          Added
        </Button>
      </DropdownMenuTrigger>
      <ItemCardEditButtonDropdownContent item={item} type={type} toggleDialog={toggleDialog} setDeleteData={setDeleteData} />
    </DropdownMenu>
  );
};

function ItemCardEditButtonDropdownContent({
  item,
  type,
  toggleDialog,
  setDeleteData,
}: {
  item: ItemCardDataModel;
  type: string;
  toggleDialog: () => void;
  setDeleteData: (data: deleteDataModel | undefined) => void;
}) {

  const actions = [
    {
      label: "Currently Watching",
      action: "watching",
      icon: <TvMinimalPlay />,
    },
    { label: "Completed", action: "completed", icon: <SquareCheckBig /> },
    { label: "On Hold", action: "on_hold", icon: <OctagonPause /> },
    { label: "Dropped", action: "dropped", icon: <BookmarkX /> },
    { label: "Plan to Watch", action: "plan_to_watch", icon: <NotebookPen /> },
    { label: "Delete", action: "delete", icon: <Trash2 /> },
  ];

  return (
    <DropdownMenuContent className="w-48">
      {actions.map(({ label, action, icon }) =>
        action !== "delete" ? (
          <DropdownMenuItem
            key={action}
            onSelect={() =>
              handleStatusUpdateAndDelete(
                action,
                type,
                item,
                toggleDialog,
                setDeleteData
              )
            }
            className="cursor-pointer">
            {icon}
            {label}
          </DropdownMenuItem>
        ) : (
          <Fragment key={action}>
            <DropdownMenuSeparator />
            <DropdownMenuItem
              onSelect={() =>
                handleStatusUpdateAndDelete(
                  action,
                  type,
                  item,
                  toggleDialog,
                  setDeleteData
                )
              }
              className="cursor-pointer">
              {icon}
              {label}
            </DropdownMenuItem>
          </Fragment>
        )
      )}
    </DropdownMenuContent>
  );
}

export default ItemCardEditButtonDropdown;
