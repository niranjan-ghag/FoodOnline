// // Initialize Google Places Autocomplete
// let autocomplete;

// function initAutoComplete() {
// autocomplete = new google.maps.places.Autocomplete(
//     document.getElementById('id_address'),
//     {
//         types: ['geocode','establishment'],
//         componentRestrictions: {'country': ['in']},
//     })
    
// autocomplete.addListener('place_changed', onPlaceChanged);
// }

// function onPlaceChanged(){
//     var place = autocomplete.getPlace();
//     console.log(place)
//     if (!place.geometry){
//         document.getElementById('id_address').placeholder = "Start Typing..";
//     }
//     else{
//         console.log('place name=>', place.name)
//     }
// }

$(document).ready(function(){
    // Add to Cart
    $('.add_to_cart').on('click',function(e){
        e.preventDefault();

        food_id = $(this).attr('data-id');
        url = $(this).attr('data-url');
        // console.log(food_id)
        // alert(food_id)
        $.ajax({
            type: 'GET',
            url: url,
            success: function(response){
                if (response.status =='login_required'){
                    // console.log(response);
                    swal(response.message,'','info').then(function(){
                        window.location = '/account/login';
                    })
                }else if (response.status =='Failed'){
                    swal(response.message,'','error')
                }
                else{
                    // console.log("---",response)
                    $('#cart_counter').html(response.cart_counter['cart_count']);
                    $('#qty-'+food_id).html(response.qty);

                    // subtotal tax & grandtotal
                    applyCartAmt(response.cart_amount['subtotal'],
                        response.cart_amount['tax_dict'],
                        response.cart_amount['grand_total']

                    )
                }
            }
        })
    })

    //place the cart item qty on load
    $('.item_qty').each(function(){
        var the_id = $(this).attr('id');
        var qty = $(this).attr('data-qty');
        $('#'+the_id).html(qty);
    })

    // Decrease Cart
    $('.decrease_cart').on('click',function(e){
        e.preventDefault();

        food_id = $(this).attr('data-id');
        url = $(this).attr('data-url');
        cart_id = $(this).attr('id');
        
        $.ajax({
            type: 'GET',
            url: url,
            success: function(response){
                // console.log(response)
                if (response.status =='login_required'){
                    swal(response.message,'','info').then(function(){
                        window.location = '/account/login';
                    })
                }else if (response.status =='Failed'){
                    $('#cart_counter').html(response.cart_counter['cart_count']);
                    $('#qty-'+food_id).html(response.qty);
                    swal(response.message,'','error')
                    
                    
                }
                else{
                    $('#cart_counter').html(response.cart_counter['cart_count']);
                    $('#qty-'+food_id).html(response.qty);

                    applyCartAmt(response.cart_amount['subtotal'],
                        response.cart_amount['tax_dict'],
                        response.cart_amount['grand_total']
                    )
                    if (window.location.pathname =='/cart/'){
                        removeCartItem(response.qty, cart_id);
                        checkEmptyCart();
                    }
                    // subtotal tax & grandtotal
                    
                }
                
               
            }
               
        })
    })

    // Delete Cart Item
    $('.delete_cart').on('click',function(e){
        e.preventDefault();

        cart_id = $(this).attr('data-id');
        url = $(this).attr('data-url');
        
        $.ajax({
            type: 'GET',
            url: url,
            success: function(response){
                // console.log(response)
                if (response.status =='Failed'){
                    // $('#cart_counter').html(response.cart_counter['cart_count']);
                    // $('#qty-'+food_id).html(response.qty);
                    swal(response.message,'','error')
                }
                else{
                    $('#cart_counter').html(response.cart_counter['cart_count']);
                    swal(response.status, response.message, 'success')

                    applyCartAmt(response.cart_amount['subtotal'],
                        response.cart_amount['tax_dict'],
                        response.cart_amount['grand_total']

                    )

                    removeCartItem(0,cart_id);
                    checkEmptyCart();
                }
            }
               
        })
    })

    // delete the cart element of the qty is 0
    function removeCartItem(cartItemQty, cart_id){
        if (cartItemQty  <=0){
            // remove cart item element
            document.getElementById('cart-item-'+cart_id).remove();
        }
    }

    function checkEmptyCart(){
        var cart_counter = document.getElementById('cart_counter').innerHTML
        if (cart_counter == 0){
            document.getElementById("empty-cart").style.display = "block"
        }
    }

    // apply cart amounts
    function applyCartAmt(subtotal, tax_dict, grand_total){
        if(window.location.pathname=='/cart/'){
            $('#subtotal').html(subtotal)
            $('#total').html(grand_total)
            for( key1 in tax_dict){
                for( key2 in tax_dict[key1]){
                    $('#tax-'+key1).html(tax_dict[key1][key2])
                }
            }
        }
        
    }

    // Add tabular structure
    $('.add_hour').on('click', function(e){
        e.preventDefault();
        var day = document.getElementById('id_days').value
        var from_hours = document.getElementById('id_from_hours').value
        var to_hours = document.getElementById('id_to_hours').value
        var is_closed = document.getElementById('id_is_closed').checked
        var csrf_token = $('input[name=csrfmiddlewaretoken]').val()
        var url = document.getElementById('add_hour_url').value
        console.log(from_hours)

        if (is_closed){
            is_closed = 'True'
            condition = "day !=''"
        }
        else{
            is_closed = 'False'
            condition = "day != '' && from_hours !='' && to_hours != '' "
        }
        if (eval(condition)){
            $.ajax({
                type: 'POST',
                url: url,
                data: {
                    'days': day,
                    'from_hours':from_hours,
                    'to_hours':to_hours,
                    'is_closed':is_closed,
                    'csrfmiddlewaretoken': csrf_token
                },
                success: function(response){
                    // console.log(response)
                    if (response.status =='success'){
                        if (response.is_closed == 'Closed'){
                            html = '<tr id="hour-'+response.id+'"><td><b>'+response.day+'</b></td><td>Closed</td><td><a href="" class="remove_hour" data-url="/vendor/opening_hours/remove/'+response.id+'">Remove</a></td></tr>'
                        }
                        else{
                            html = '<tr id="hour-'+response.id+'"><td><b>'+response.day+'</b></td><td>'+response.from_hours+' - '+ response.to_hours+'</td><td><a href="" class="remove_hour" data-url="/vendor/opening_hours/remove/'+response.id+'">Remove</a></td></tr>'
                        }
                        
                        $(".opening_hours").append(html)
                        document.getElementById("opening_hours").reset();
                    }
                    else{
                        console.log(response.message)
                        swal(response.message,'','error')
                    }
                }
            })
        }
        else{
            swal('Please fill all the fields!','','info')
        }

    })

    // Remove hours
    // $('.remove_hour').on('click', function(e){
    //     e.preventDefault();
    //     url = $(this).attr('data-url');
        
    //     $.ajax({
    //         type: 'GET',
    //         url: url,
    //         success: function(response){
    //             if(response.status == 'success'){
    //                 document.getElementById('hour-'+response.id).remove()
    //             }
    //         }
    //     })

    // })

    $(document).on('click','.remove_hour', function(e){
        e.preventDefault();
        url = $(this).attr('data-url');
        
        $.ajax({
            type: 'GET',
            url: url,
            success: function(response){
                if(response.status == 'success'){
                    document.getElementById('hour-'+response.id).remove()
                }
            }
        })
    })

    // document ready close
})