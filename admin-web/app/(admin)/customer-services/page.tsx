"use client";

import {
  createCustomerService,
  deleteCustomerService,
  getCustomerServiceList,
  updateCustomerService,
} from "@/lib/api";
import { StaffManagementPage } from "../staff-management-page";


export default function Page() {
  return (
    <StaffManagementPage
      createItem={createCustomerService}
      createText="新增客服"
      deleteItem={deleteCustomerService}
      entityName="客服"
      getList={getCustomerServiceList}
      title="客服管理"
      updateItem={updateCustomerService}
    />
  );
}
