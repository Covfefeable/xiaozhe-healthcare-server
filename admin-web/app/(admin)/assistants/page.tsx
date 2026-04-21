"use client";

import {
  createAssistant,
  deleteAssistant,
  getAssistantList,
  updateAssistant,
} from "@/lib/api";
import { StaffManagementPage } from "../staff-management-page";


const assistantTypeOptions = [
  { label: "健康管家", value: "health_manager" as const },
  { label: "医疗助理", value: "medical_assistant" as const },
];


export default function Page() {
  return (
    <StaffManagementPage
      staffTypeOptions={assistantTypeOptions}
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
