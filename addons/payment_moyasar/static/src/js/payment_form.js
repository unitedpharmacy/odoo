$(document).ready(function() {
    $("#pay_form").removeClass("noClick");

    $("[name='delete_card_info']").click(function(e) {
        e.preventDefault();
        var select_card = $("input[type='radio'][name='select_card']:checked").val();
        $.ajax({
            type: "POST",
            url: "/payment/moyasar/delete/",
            "headers": {
                "Content-Type": "application/x-www-form-urlencoded"
            },
            data: {
                id: select_card,
            },
            success: function(data) {
                var success_msg = "Card was deleted successfully."
                $("#out_div_" + select_card).replaceWith('<div class="alert alert-success alert-dismissible fade show" role="alert"><strong>' + success_msg + '<button type="button" class="close" data-dismiss="alert" aria-label="Close"><span >&times;</span></button></div>');
            },
            error: function(data) {
                var error_msg = "Failed to delete the card.";
                $("#out_div_" + select_card).append('<div class="alert alert-danger alert-dismissible fade show" role="alert"><strong>' + error_msg + '<button type="button" class="close" data-dismiss="alert" aria-label="Close"><span >&times;</span></button></div>');
            },
        });
    });


    $("[name='select_card']").change(function() {
        $("[name='select_card']").each(function() {
            $('#person_name_' + $(this).val()).prop('required', false);
            $('#card_number_' + $(this).val()).prop('required', false);
            $('#cvc_' + $(this).val()).prop('required', false);
            $('#year_' + $(this).val()).prop('required', false);
            $('#month_' + $(this).val()).prop('required', false);
            $('#div_' + $(this).val()).prop('hidden', true);
        });

        if ($(this).is(':checked')) {
            $('#person_name_' + $(this).val()).prop('required', true);
            $('#card_number_' + $(this).val()).prop('required', true);
            $('#cvc_' + $(this).val()).prop('required', true);
            $('#year_' + $(this).val()).prop('required', true);
            $('#month_' + $(this).val()).prop('required', true);
            $('#div_' + $(this).val()).prop('hidden', false);
        }
    });

    $('#pay_form').submit(function(e) {
        e.preventDefault();
        var select_card = $("input[type='radio'][name='select_card']:checked").val();
        if (select_card) {

            var today = new Date();
            var current_month = today.getMonth() + 1;
            var current_year = today.getYear().toString().substr(-2);
            if ((current_year == $("#year_" + select_card).val()) && (current_month > $("#month_" + select_card).val())) {
                $("#validation").append('<div class="alert alert-danger alert-dismissible fade show" role="alert"><strong>Validation Failed: </strong>Card is expired.<button type="button" class="close" data-dismiss="alert" aria-label="Close"><span >&times;</span></button></div>');
            } else {
                $.ajax({
                    type: "POST",
                    url: "https://api.moyasar.com/v1/payments",
                    "headers": {
                        "Authorization": "Basic c2tfdGVzdF9XakxDZmZteTVZenNrVkxSalVDSExjMXFaOXc5dGE5aFNlOVdYejN6Og==",
                        "Content-Type": "application/x-www-form-urlencoded"
                    },
                    data: {
                        amount: amount * 100,
                        description: reference,
                        currency: currency,
                        source: ({
                            type: "creditcard",
                            name: $("#person_name_" + select_card).val(),
                            number: $("#card_number_" + select_card).val(),
                            cvc: $("#cvc_" + select_card).val(),
                            month: $("#month_" + select_card).val(),
                            year: $("#year_" + select_card).val(),
                        }),
                        callback_url: CALLBACK_URL
                    },
                    success: function(data) {

                        if (document.getElementById("save_card_info").checked) {
                            $.ajax({
                                type: "POST",
                                url: "/payment/moyasar/save/",
                                "headers": {
                                    "Content-Type": "application/x-www-form-urlencoded"
                                },
                                data: {
                                    name: $("#person_name_" + select_card).val(),
                                    number: $("#card_number_" + select_card).val(),
                                    month: $("#month_" + select_card).val(),
                                    year: $("#year_" + select_card).val(),
                                },
                            });
                        }

                        window.location.href = data.source.transaction_url
                    },
                    error: function(data) {
                        var error_type = data.responseJSON.message;
                        var error_msg = Object.keys(data.responseJSON.errors)[0] + " " + Object.values(data.responseJSON.errors)[0];
                        $("#validation").append('<div class="alert alert-danger alert-dismissible fade show" role="alert"><strong>' + error_type + ': </strong>' + error_msg + '.<button type="button" class="close" data-dismiss="alert" aria-label="Close"><span >&times;</span></button></div>');
                    },
                });
            }
        }
    })
})