#include <core.p4>
#if __TARGET_TOFINO__ == 2
#include <t2na.p4>
#else
#include <tna.p4>
#endif

#include "headers.p4"
#include "util.p4"

struct metadata_t {
    bit<32> threshold;
    bit<16> res_all;
    
    stub_1

    bit<1> above_threshold;
}

#include "parser.p4"
#define ETHERTYPE_TO_CPU 0xBF01
#define ETHERTYPE_TO_CPU 0xBF01
    
const PortId_t CPU_PORT = 192; // tofino with pipeline 2
// const PortId_t CPU_PORT = 320; // tofino with pipeline 4

control GET_THRESHOLD(
    inout header_t hdr,
    inout metadata_t ig_md)
{
    action tbl_get_threshold_act (bit<32> threshold) {
        ig_md.threshold = threshold;
    }
    table tbl_get_threshold {
        key = {
            hdr.ethernet.ether_type : exact;
        }
        actions = {
            tbl_get_threshold_act;
        }
    }
    apply {
        tbl_get_threshold.apply();
    }
}


control heavy_flowkey_storage (
    inout header_t hdr,
    inout metadata_t ig_md,
    inout ingress_intrinsic_metadata_for_tm_t ig_tm_md)
{
    // threshold table
    action tbl_threshold_above_action() {
        ig_md.above_threshold = 1;
    }

    table tbl_threshold {
        key = {
            stub_2
        }
        actions = {
            tbl_threshold_above_action;
        }
    }

    // hash table
    // bit<32> : entry size
    // bit<16> : index size
    // 65536   : SRAM size
                                    
    stub_3 

    RegisterAction<bit<32>, bit<16>, bit<32>>(flowkey_hash_table) flowkey_action = {
        void apply(inout bit<32> register_data, out bit<32> result) {
            if (register_data == 0) {
                register_data = hdr.ipv4.src_addr;
                result = 0;
            }
            else {
                result = register_data;
            }
        }
    };

    // exact table
    action tbl_exact_match_miss() {
        hdr.cpu_ethernet.setValid();
        hdr.cpu_ethernet.dst_addr   = 0xFFFFFFFFFFFF;
        hdr.cpu_ethernet.src_addr   = 0xAAAAAAAAAAAA;
        hdr.cpu_ethernet.ether_type = ETHERTYPE_TO_CPU;
        ig_tm_md.ucast_egress_port = CPU_PORT;
    }

    action tbl_exact_match_hit() {
    }

    table tbl_exact_match {
        key = {
            hdr.ipv4.src_addr : exact;
        }
        actions = {
            tbl_exact_match_miss;
            tbl_exact_match_hit;
        }
        const default_action = tbl_exact_match_miss;
        stub_4
    }

    apply {

        stub_5

        tbl_threshold.apply();

        if(ig_md.above_threshold == 1) {
            // bit<32> hash_entry = flowkey_action.execute(ig_md.res_all[1:0]);
            bit<32> hash_entry = flowkey_action.execute(ig_md.res_all[15:0]);

            if (hash_entry != 0) {
                if (hash_entry != hdr.ipv4.src_addr) {
                    tbl_exact_match.apply();
                }
            }
            // alternatively, we can read flowkey from flowkey_hash_table in the control plane
            // else {
            //     tbl_exact_match_miss();
            // }
        }
    }
}

control CM_UPDATE(
  in bit<32> key,
  out bit<32> est)(
  bit<32> polynomial)
{
    CRCPolynomial<bit<32>>(polynomial,                          
                         true,                                  
                         false,                                 
                         false,                                 
                         32w0xFFFFFFFF,                         
                         32w0xFFFFFFFF                          
                         ) poly1;                               
                                                                
    Hash<bit<16>>(HashAlgorithm_t.CUSTOM, poly1) hash;//...................hash_call: hash_init

    stub_6 

    RegisterAction<bit<32>, bit<16>, bit<32>>(cm_table) cm_action = {
        void apply(inout bit<32> register_data, out bit<32> result) {
            register_data = register_data + 1;
            result = register_data;
        }//...................register_update: register_update
    };

    apply {
        est = cm_action.execute(hash.get({key}));
    }
}


control SwitchIngress(
        inout header_t hdr,
        inout metadata_t ig_md,
        in ingress_intrinsic_metadata_t ig_intr_md,
        in ingress_intrinsic_metadata_from_parser_t ig_prsr_md,
        inout ingress_intrinsic_metadata_for_deparser_t ig_dprsr_md,
        inout ingress_intrinsic_metadata_for_tm_t ig_tm_md) {
    
    stub_7


    heavy_flowkey_storage() store_flowkey;

    GET_THRESHOLD() get_threshold;

    apply {

        if(hdr.ethernet.ether_type == ETHERTYPE_IPV4) {

            get_threshold.apply(hdr, ig_md);

            stub_8

            store_flowkey.apply(hdr, ig_md, ig_tm_md);

       }
    }
}

struct my_egress_headers_t {
}

    /********  G L O B A L   E G R E S S   M E T A D A T A  *********/

struct my_egress_metadata_t {
}

parser EgressParser(packet_in        pkt,
    /* User */
    out my_egress_headers_t          hdr,
    out my_egress_metadata_t         meta,
    /* Intrinsic */
    out egress_intrinsic_metadata_t  eg_intr_md)
{
    /* This is a mandatory state, required by Tofino Architecture */
    state start {
        pkt.extract(eg_intr_md);
        transition accept;
    }
}

control EgressDeparser(packet_out pkt,
    /* User */
    inout my_egress_headers_t                       hdr,
    in    my_egress_metadata_t                      meta,
    /* Intrinsic */
    in    egress_intrinsic_metadata_for_deparser_t  eg_dprsr_md)
{
    apply {
        pkt.emit(hdr);
    }
}

Pipeline(
    SwitchIngressParser(),
    SwitchIngress(),
    SwitchIngressDeparser(),
    EgressParser(),
    EmptyEgress(),
    EgressDeparser()
) pipe;

Switch(pipe) main;

