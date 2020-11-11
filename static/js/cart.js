var updateBtns = document.getElementsByClassName('update-cart')

for(var i = 0; i < updateBtns.length; i++){
    updateBtns[i].addEventListener('click',function(){
        var productId = this.dataset.product
        var action = this.dataset.action
        console.log('productId:', productId, 'action:', action)
        updateUserorder(productId, action);
        console.log('user:', user)
        /*if(user == 'AnonymousUser'){
            console.log('Not logged in')
        }else{
            console.log('User logged in, Sending data..')
            updateUserorder(productId, action);
        }*/

    })
}

function updateUserorder(productId, action){
    console.log('User Authenticated, Sending data..')
    var url = '/updateitem/'

    fetch(url, {
        method :'POST',
        headers:{
            'Content-Type':'application/json',
            'X-CSRFToken':csrfToken,
        },
        body:JSON.stringify({'productId':productId, 'action':action})
    })
    .then((response) =>{
        return response.json()
    })
    .then((data) =>{
        console.log('data:', data)
        location.reload()
    })
}