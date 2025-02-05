document.addEventListener("DOMContentLoaded", function() {
    const proceedButton = document.getElementById("proceed-button");
    const pricingFormContainer = document.getElementById("pricing-form-container");
    const confirmButton = document.getElementById("Confirm");
    const submitDetails = document.getElementById("submit-details");
    const finalsubmitButton = document.getElementById('final-submit-button');

    // Show the pricing form when Proceed button is clicked
    proceedButton.addEventListener("click", function() {
        const selectedCollege = document.getElementById("college").value;

        if (selectedCollege) {
            pricingFormContainer.style.display = "block";
        } else {
            alert("Please select a college to proceed.");
        }
    });

    // Calculate the price and show the pricing breakdown
    document.getElementById("pricing-calculator").addEventListener("submit", function(event) {
        event.preventDefault();

        const type = document.getElementById("type").value;
        const urgency = document.getElementById("urgency").value;
        const asstype = document.getElementById("asstype").value;
        const length = parseInt(document.getElementById("length").value);
        const pages = parseInt(document.getElementById("pages").value);
        const details = document.getElementById("details").value;

        let price = 0;

        // Calculate based on word count
        if (length <= 200 && pages == 1) {
            price += 200; // Base price for 1 page (200 words)
        } else {
            // Calculate pages for word count
            price += 200 + pages * 50; // Multiply by ₹40 per page
        }

        // Adjust based on urgency
        if (urgency === "urgent") {
            price *= 1.5; // 50% increase for urgent
        } else if (urgency === "express") {
            price *= 1.3; // 30% increase for express
        } else {
            price *= 1.1; // 10% increase for standard
        }

        // Additional fees for extra details
        let additionalFees = 0;
        if (details) {
            additionalFees = 0; // Fixed fee for additional details
            price += additionalFees;
        }

        // Show the price breakdown in the table
        document.getElementById("college-result").innerText = document.getElementById("college").value;
        document.getElementById("type-result").innerText = type;
        document.getElementById("urgency-result").innerText = urgency;
        document.getElementById("asstype-result").innerText = asstype;
        document.getElementById("length-result").innerText = length + " words";
        document.getElementById("pages-result").innerText = pages + " pages";
        document.getElementById("detail-result").innerText = details;
        //document.getElementById("additional-fees").innerText = "₹" + additionalFees;
        //document.getElementById("total-price").innerText = "₹" + price.toFixed(2); // Display total price with 2 decimal places
        document.getElementById("price-table").style.display = "block";
    });

    // Show the email and phone number form when Confirm button is clicked
    confirmButton.addEventListener("click", function() {
        submitDetails.style.display = "block";
    });

});


const loginText = document.querySelector(".title-text .login");
const loginForm = document.querySelector("form.login");
const loginBtn = document.querySelector("label.login");
const signupBtn = document.querySelector("label.signup");
const signupLink = document.querySelector("form .signup-link a");
signupBtn.onclick = (() => {
    loginForm.style.marginLeft = "-50%";
    loginText.style.marginLeft = "-50%";
});
loginBtn.onclick = (() => {
    loginForm.style.marginLeft = "0%";
    loginText.style.marginLeft = "0%";
});
signupLink.onclick = (() => {
    signupBtn.click();
    return false;
});