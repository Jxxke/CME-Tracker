document.addEventListener('DOMContentLoaded', function() {
    const stateField = document.getElementById('id_state');
    const licenseTypeField = document.getElementById('id_license_type');

    stateField.addEventListener('change', populateDefaults);
    licenseTypeField.addEventListener('change', populateDefaults);

    function populateDefaults() {
        const state = stateField.value;
        const licenseType = licenseTypeField.value;

        if (state && licenseType) {
            fetch(`/ajax/get_cme_defaults/?state=${state}&license_type=${licenseType}`)
                .then(response => response.json())
                .then(data => {
                    if (data.renewal_period_years) {
                        document.getElementById('id_renewal_period_years').value = data.renewal_period_years;
                        document.getElementById('id_total_cme_required').value = data.total_cme_required;
                        document.getElementById('id_special_cme_category').value = data.special_cme_category;
                        document.getElementById('id_special_cme_hours_required').value = data.special_cme_hours_required;
                    }
                })
                .catch(() => {
                    console.log("No defaults found for selected state/license.");
                });
        }
    }
});
