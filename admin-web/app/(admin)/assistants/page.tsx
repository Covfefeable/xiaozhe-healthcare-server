"use client";

import {
  createAssistant,
  deleteAssistant,
  getAssistantList,
  updateAssistant,
} from "@/lib/api";
import { StaffManagementPage } from "../staff-management-page";


export default function Page() {
  return (
    <StaffManagementPage
      createItem={createAssistant}
      createText="新增助理"
      deleteItem={deleteAssistant}
      entityName="助理"
      getList={getAssistantList}
      title="助理管理"
      updateItem={updateAssistant}
    />
  );
}
