use std::collections::{HashMap, HashSet};
use std::fs::File;
use std::io::BufReader;
use std::path::PathBuf;

use quick_xml::{Error, Reader};
use quick_xml::events::attributes::Attributes;
use quick_xml::name::QName;

pub(crate) fn panic_read_file(msd_file_reader: &mut Reader<BufReader<File>>, e: Error) {
    panic!("Error at position {}: {:?}", msd_file_reader.buffer_position(), e)
}

pub(crate) fn panic_unexpected_eof_read_file(msd_file_reader: &mut Reader<BufReader<File>>) {
    panic!("Error at position {}: Unexpected EOF!", msd_file_reader.buffer_position())
}

pub(crate) fn convert_to_string(path_buf_to_msd_file: &PathBuf) -> String {
    path_buf_to_msd_file.to_str().unwrap().to_string()
}

pub(crate) fn get_value_of_attribute_with_key(attributes: Attributes, attribute_name: &str) -> Option<String> {
    get_values_of_attributes_with_keys(attributes, vec![attribute_name]).remove(attribute_name)
}

pub(crate) fn get_values_of_attributes_with_keys(attributes: Attributes, attribute_names: Vec<&str>) -> HashMap<String, String> {
    let attribute_names_set: HashSet<&str> = attribute_names.into_iter().collect();
    let mut key_value_map = HashMap::new();
    for attribute in attributes {
        let unwrapped_attribute = attribute.unwrap();
        let key = convert_qname_to_string(&unwrapped_attribute.key);
        if attribute_names_set.contains(&key.as_str()) {
            key_value_map.insert(key, unwrapped_attribute.unescape_value().unwrap().to_string());
        }
    }
    return key_value_map;
}

pub(crate) fn convert_qname_to_string(qname: &QName) -> String {
    String::from_utf8(qname.as_ref().to_vec()).unwrap()
}

#[cfg(test)]
mod tests {
    use quick_xml::name::QName;

    use crate::builder::builder_helper::convert_qname_to_string;

    #[test]
    fn test_convert_qname_to_string() {
        // given
        let qname = QName("test_q_name".as_bytes());

        //when
        let converted_string = convert_qname_to_string(&qname);

        //assert
        assert_eq!(converted_string, "test_q_name");
    }
}
