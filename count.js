function count(){
			var phrases = document.getElementById('keywords').value;
			alert(phrases);
			var words_list = phrases.split(' ');
			var words_dict = {};

			if(words_list.length <= 1){
				document.getElementById('results').innerHTML = phrases;
				//alert(phrases.length);
			}
			else{
				words_list.forEach(value => words_dict = (words_dict[value] || 0) + 1);
				document.getElementById('results').innerHTML = words_dict;
			}
		}
