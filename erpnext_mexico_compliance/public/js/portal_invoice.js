// Copyright (c) 2025, TI Sin Problemas and contributors
// For license information, please see license.txt

frappe.ready(() => {
  if (window.location.pathname.includes("/invoices/")) {
    const menuItem = document.createElement("a");
    menuItem.classList.add("dropdown-item");
    menuItem.innerText = __("Download CFDI files");

    menuItem.onclick = () => {
      const docname = window.location.pathname.split("/").pop();
      window.location.href = `/api/method/erpnext_mexico_compliance.api.v1.download_cfdi_files?doctype=Sales%20Invoice&docname=${docname}`;
    };

    const dropdownMenu = document.querySelector(
      ".page-header-actions-block .row .dropdown-menu"
    );
    dropdownMenu.appendChild(menuItem);
  }
});
