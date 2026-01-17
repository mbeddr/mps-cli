use std::collections::HashMap;

pub(crate) struct NodeIdEncodingUtils {
    my_index_chars : String,
    min_char : u8,
    my_char_to_value : HashMap<usize, usize>,       
}

impl NodeIdEncodingUtils {
    pub(crate) fn new() -> Self {
        let my_index_chars = String::from("0123456789abcdefghijklmnopqrstuvwxyz$_ABCDEFGHIJKLMNOPQRSTUVWXYZ");
        let min_char = '$' as u8;
        let mut my_char_to_value : HashMap<usize, usize> = HashMap::new();
        let bytes = my_index_chars.as_bytes();
        for i in 0..my_index_chars.len() {
            let char_value = bytes[i] as u8;
            let ii: usize = (char_value - min_char) as usize;
            my_char_to_value.insert(ii, i);
        }

        NodeIdEncodingUtils {
            my_index_chars : my_index_chars,
            min_char : min_char,
            my_char_to_value : my_char_to_value,
        }
    }
    // transforms from a string representing java friendly base 64 encoding 
    //  a string representing its decimal encoding
    pub(crate) fn decode(&self, uid_string : String) -> String {
        let mut res = 0;
        let bytes = uid_string.as_bytes();
        let mut c = bytes[0];
        let ii : usize = (c as u8 - self.min_char) as usize;
        let mut value = self.my_char_to_value[&ii];
        res = value;
        for idx in 1..uid_string.len() {
            res = res << 6;
            c = bytes[idx];
            value = self.my_index_chars.find(c as char).unwrap();
            res = res | value;
        }
        return res.to_string();
    }

    // transforms from a string representing a decimal number to 
    //  a string representing its java friendly base 64 encoding
    pub(crate) fn encode(&self, uid_string : String) -> String {
        let uid_number = match uid_string.parse::<u64>() {
            Ok(val) => val,
            Err(_) => return String::from("Invalid decimal input"),
        };

        let mut num = uid_number;
        let mut res_size = 0;
        while num > 0 {
            res_size += 1;
            num /= 64;
        }
        if res_size == 0 {
            res_size = 1;
        }
        let mut res: Vec<char> = Vec::with_capacity(res_size as usize);

        let mut num = uid_number;
        while num > 0 {
            let pos = num % 64;
            let crt_char= self.my_index_chars.chars().nth(pos as usize).unwrap();
            res.push(crt_char);
            num /= 64;
        }

        res.reverse();
        let res: String = res.into_iter().collect();
        return res;
    }

}
    
#[cfg(test)]
mod tests {
    use crate::builder::node_id_utils::NodeIdEncodingUtils;

    #[test]
    fn test_conversion() {
        let node_id_utils = NodeIdEncodingUtils::new();

        assert_eq!("5731700211660045983", node_id_utils.decode(String::from("4Yb5JA31NUv")));
        assert_eq!("4Yb5JA31NUv", node_id_utils.encode(String::from("5731700211660045983")));
    }
}   