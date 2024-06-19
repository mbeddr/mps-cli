use std::collections::HashMap;


struct NodeIdEncodingUtils {
    myIndexChars : String,
    min_char : u8,
    myCharToValue : HashMap<usize, usize>,
        
}

impl NodeIdEncodingUtils {
    pub(crate) fn new() -> Self {
        let my_index_chars = String::from("0123456789abcdefghijklmnopqrstuvwxyz$_ABCDEFGHIJKLMNOPQRSTUVWXYZ");
        let min_char = '$' as u8;
        let mut myCharToValue : HashMap<usize, usize> = HashMap::new();
        let bytes = my_index_chars.as_bytes();
        for i in 0..my_index_chars.len() {
            let char_value = bytes[i] as u8;
            let ii: usize = (char_value - min_char) as usize;
            myCharToValue.insert(ii, i);
        }

        NodeIdEncodingUtils {
            myIndexChars : my_index_chars,
            min_char : min_char,
            myCharToValue : myCharToValue,
        }
    }

    pub(crate) fn decode(&self, uid_string : String) -> String {
        let mut res = 0;
        let bytes = uid_string.as_bytes();
        let mut c = bytes[0];
        let ii : usize = (c as u8 - self.min_char) as usize;
        let mut value = self.myCharToValue[&ii];
        res = value;
        for idx in 1..uid_string.len() {
            res = res << 6;
            c = bytes[idx];
            value = self.myIndexChars.find(c as char).unwrap();
            res = res | value;
        }
        return res.to_string();
    }

}
    
#[cfg(test)]
mod tests {
    use crate::builder::node_id_utils::NodeIdEncodingUtils;

    #[test]
    fn test_conversion() {
        let node_id_utils = NodeIdEncodingUtils::new();

        assert_eq!("5731700211660045983", node_id_utils.decode(String::from("4Yb5JA31NUv")));
    }
}   