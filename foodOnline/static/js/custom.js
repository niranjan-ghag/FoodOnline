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
                    console.log(response);
                    swal(response.message,'','info').then(function(){
                        window.location = '/account/login';
                    })
                }else if (response.status =='Failed'){
                    swal(response.message,'','error')
                }
                else{
                    console.log("---",response)
                    $('#cart_counter').html(response.cart_counter['cart_count']);
                    $('#qty-'+food_id).html(response.qty);

                    // subtotal tax & grandtotal
                    applyCartAmt(response.cart_amount['subtotal'],
                        response.cart_amount['tax'],
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
                        response.cart_amount['tax'],
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
                console.log(response)
                if (response.status =='Failed'){
                    // $('#cart_counter').html(response.cart_counter['cart_count']);
                    // $('#qty-'+food_id).html(response.qty);
                    swal(response.message,'','error')
                }
                else{
                    $('#cart_counter').html(response.cart_counter['cart_count']);
                    swal(response.status, response.message, 'success')

                    applyCartAmt(response.cart_amount['subtotal'],
                        response.cart_amount['tax'],
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
    function applyCartAmt(subtotal, tax, grand_total){
        if(window.location.pathname=='/cart/'){
            $('#subtotal').html(subtotal)
            $('#tax').html(tax)
            $('#total').html(grand_total)
        }
        
    }

})