jQuery.validator.addMethod("validate_zip", function(value, element) {
    if (typeof value !== "string" || value.length < 4) {
        return false;
    }

    // Check if the first 4 characters are digits
    var firstFourChars = value.substr(0, 4);
    return /^\d{4}$/.test(firstFourChars);
}, 'Postal Code Invalid');

jQuery.validator.addMethod("validate_phone_number", function(value, element) {
    if (value === "") {
        return true;
    }

    var numericValue = value.replace(/\D/g, ""); // Replace non-numeric characters

    return /^\d+$/.test(numericValue) && numericValue.length >= 10 && numericValue.length <= 13;
}, 'Phone Number Invalid');


jQuery.validator.addMethod("validate_state", function(value, element) {
    var validStateAbbreviations = ['AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA', 'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD', 'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY', 'DC', 'MH', 'PR'];

    if (validStateAbbreviations.includes(value)) {
        return true;
    } else {
        return false
    }
}, 'State Invalid');