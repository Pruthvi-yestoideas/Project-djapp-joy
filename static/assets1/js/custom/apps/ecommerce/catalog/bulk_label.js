"use strict";
var KTAppEcommerceProducts = function () {
    var t, e, n = () => {

    }; return {
        init: function () {
            (t = document.querySelector("#kt_ecommerce_products_table")) && ((e = $(t).DataTable({
                paging: false,
                info: !1, order: [], columnDefs: [{
                }, { orderable: !1, targets: 0 }, {
                    orderable: !1, targets: 7
                }]
            })).on("draw", (function () { n() })), document.querySelector('[data-kt-ecommerce-product-filter="search"]').addEventListener("keyup", (function (t) {
                e.search(t.target.value).draw()
            })), (() => {

            })(), n())
            
            var initToggleToolbar = function () {
                // Toggle selected action toolbar
                // Select all checkboxes
                const container = document.querySelector('#kt_ecommerce_products_table');
                const checkboxes = container.querySelectorAll('[type="checkbox"]');
        
                // Select elements
                const deleteSelected = document.querySelector('[data-kt-docs-table-select="delete_selected"]');
        
                // Toggle delete selected toolbar
                checkboxes.forEach(c => {
                    // Checkbox on click event
                    c.addEventListener('click', function () {
                        setTimeout(function () {
                            toggleToolbars();
                        }, 50);
                    });
                });
            }
            // Define 
            var toggleToolbars = function () {
                const container = document.querySelector('#kt_ecommerce_products_table');
                const toolbarBase = document.querySelector('[data-kt-docs-table-toolbar="base"]');
                const toolbarSelected = document.querySelector('[data-kt-docs-table-toolbar="selected"]');
                const selectedCount = document.querySelector('[data-kt-docs-table-select="selected_count"]');
                // Select refreshed checkbox DOM elements
                const allCheckboxes = container.querySelectorAll('tbody [type="checkbox"]');
                // Detect checkboxes state & count
                let checkedState = false;
                let count = 0;
    
                // Count checked boxes
                allCheckboxes.forEach(c => {
                    if (c.checked) {
                        checkedState = true;
                        count++;
                    }
                });
    
                // Toggle toolbars
                if (checkedState) {
                    selectedCount.innerHTML = count;
                    toolbarBase.classList.add('d-none');
                    toolbarSelected.classList.remove('d-none');
                } else {
                    toolbarBase.classList.remove('d-none');
                    toolbarSelected.classList.add('d-none');
                }
            }
               // Toggle toolbars
            initToggleToolbar();
            toggleToolbars();
            document.querySelectorAll('[data-kt-ecommerce-product-filter="delete_row"]').forEach((delete_btn => {
                delete_btn.addEventListener("click", (function (t) {
                    t.preventDefault(); const n = t.target.closest("tr"); Swal.fire({
                        text: "Are you sure you want to delete?", icon: "warning", showCancelButton: !0, buttonsStyling: !1, confirmButtonText: "Yes, delete!", cancelButtonText: "No, cancel", customClass: {
                            confirmButton: "btn fw-bold btn-danger", cancelButton: "btn fw-bold btn-active-light-primary"
                        }
                    }).then((function (t) {
                        t.value ? Swal.fire({
                            text: "You have deleted!.", icon: "success", buttonsStyling: !1, confirmButtonText: "Ok, got it!", customClass: {
                                confirmButton: "btn fw-bold btn-primary"
                            }
                        }).then((
                            function () {
                                e.row($(n)).remove().draw();
                                let row_index = delete_btn.getAttribute("data-row-index");
                                address_sheet[row_index] = 0;
                                delete errors[row_index];
                                localStorage.setItem("address_sheet", JSON.stringify(address_sheet));

                                if (services.length > 0) {
                                    services[row_index] = 0;
                                }

                                for (var i=0; i<details_err.length; i++) {
                                    if (details_err[i] != 0){
                                        let row = details_err[i][0][0]
                                    
                                        if (row == row_index) {
                                            details_err[i] = 0;
                                        }
                                    }
                                }
                                calculateTotalRateAndNames(services)
                                localStorage.setItem("details_err", JSON.stringify(details_err));
                                const toolbarBase = document.querySelector('[data-kt-docs-table-toolbar="base"]');
                                const toolbarSelected = document.querySelector('[data-kt-docs-table-toolbar="selected"]');
                                toolbarBase.classList.remove('d-none');
                                toolbarSelected.classList.add('d-none');
                                $('input:checkbox').prop('checked', false);
                            })) : "cancel" === t.dismiss && Swal.fire({
                            text: "row was not deleted.", icon: "error", buttonsStyling: !1, confirmButtonText: "Ok, got it!", customClass: { confirmButton: "btn fw-bold btn-primary" }
                        })
                    }))
                }))
            }))

            var bulkDeleteBtn = document.getElementById("bulk_delete");
            bulkDeleteBtn.addEventListener("click", function (event) {
                event.preventDefault();
                // Array to store the selected rows
                let selectedRows = [];
            
                // Iterate through all checkboxes
                $('input[name="row_checks"]:checked').each(function () {
                    // Push the closest 'tr' element (row) to the selectedRows array
                    selectedRows.push($(this).closest('tr')[0]);
                });
            
                // Show confirmation modal for bulk delete
                Swal.fire({
                    text: "Are you sure you want to delete the selected items?",
                    icon: "warning",
                    showCancelButton: true,
                    buttonsStyling: false,
                    confirmButtonText: "Yes, delete!",
                    cancelButtonText: "No, cancel",
                    customClass: {
                        confirmButton: "btn fw-bold btn-danger",
                        cancelButton: "btn fw-bold btn-active-light-primary",
                    },
                }).then(function (result) {
                    if (result.value) {
                        // Perform bulk delete
                        selectedRows.forEach(function (row) {
                            // Perform any additional actions if needed
                            let row_index = row.getAttribute('data-row-index');
                            address_sheet[row_index] = 0;
                            delete errors[row_index];
                            localStorage.setItem("address_sheet", JSON.stringify(address_sheet));

                            if (services.length > 0) {
                                services[row_index] = 0;
                            }
                            
                            for (var i=0; i<details_err.length; i++) {
                                if (details_err[i] != 0){
                                    let row = details_err[i][0][0]
                                
                                    if (row == row_index) {
                                        details_err[i] = 0;
                                    }
                                }
                            }

                            localStorage.setItem("details_err", JSON.stringify(details_err));
                            // Remove the row from DataTable
                            e.row($(row)).remove();
                            const toolbarBase = document.querySelector('[data-kt-docs-table-toolbar="base"]');
                            const toolbarSelected = document.querySelector('[data-kt-docs-table-toolbar="selected"]');
                            toolbarBase.classList.remove('d-none');
                            toolbarSelected.classList.add('d-none');
                            $('input:checkbox').prop('checked', false);

                        });
                        calculateTotalRateAndNames(services)
                        // Redraw the DataTable
                        e.draw();
            
                        // Additional actions if needed (update arrays, local storage, etc.)
                    }
                });
            });
        }
    }
}(); KTUtil.onDOMContentLoaded((function () { }));
