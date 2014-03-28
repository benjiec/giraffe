// Requires: 
//    jquery-ui 1.9.2
//    jquery 1.9
//    draw.js
//
// Restriction: can only have one instance of this per DOM
//
// Depends on draw.js for the following (at least):
//    Feature
//    Feature.other_cutters
//    all_features
//    std_features
//    enzyme_features
//    orf_features
//
//
// Call:
//    GiraffeAnalyze2(jQuery,gd,{...});
//  or
//    jQuery(document).ready(function($){
//        GiraffeAnalyze2($,gd,{...});
//    })
//
// Options:
//    dom_id: dom ID to attach the analyzer window
//    map_width: map width
//    map_height: map height
//    analyzer_width: main width of the entire analyzer
//    linear_map: if 1, switch to linear map to start (default is 0, and uses circular map)
//    exclude_layers: list of layers to exclude on start
// 

(function(){

function random_dom_id() {
    return 'giraffe-'+Math.floor(Math.random()*100000000);
}

window.GiraffeAnalyze2 = function ($,gd,options) {
    var dom_id = 'giraffe-analyze';
    if ('dom_id' in options) { dom_id = options.dom_id; }
    var name = 'Sequence';
    if ('name' in options) { name = options.name; }
    var map_width = 640;
    if ('map_width' in options) { map_width = options.map_width; }
    var map_height = 640;
    if ('map_height' in options) { map_height = options.map_height; }
    var analyzer_width = 1340;
    if ('analyzer_width' in options) { analyzer_width = options.analyzer_width; }
    var starts_with_linear_map = false;
    if ('linear_map' in options && options.linear_map) { starts_with_linear_map = true; }
    var exclude_layers = [];
    if ('exclude_layers' in options) { exclude_layers = options.exclude_layers; }

    var viewer_segs_per_line = 5;

    var seqlen = gd.sequence.length;
    var sequence = new BioJS2.DNASequence(gd.sequence);
    var cutters = new Cutter_List(gd.enzyme_features);

    function Switch_Panes(panes) {
        var divs = [];
        var links = [];
        var current_pane;

        function hide_all() {
            var i;
            for (i = 0; i < divs.length; i++) { $(divs[i]).hide(); } 
            for (i = 0; i < links.length; i++) { $(links[i]).removeClass('giraffe-link-on'); } 
            current_pane = undefined;
        }
        function show(i) {
            hide_all();
            $(links[i]).addClass('giraffe-link-on');
            $(divs[i]).show();
            current_pane = parseInt(i, 10);
        }
        function link(i) { return links[i]; }
        function pane(i) { return divs[i]; }
        function current() { return current_pane; }

        var links_dom = $('<p></p>');
        var divs_dom = $('<div></div>');

        function pane_click(evt) {
                evt.preventDefault();
                var i = $(this).attr('pane'); show(i);
        }
        for (var i = 0; i < panes.length; i++) {
            var link_text = panes[i];
            var link_title;

            if (typeof panes[i] == typeof []) {
                link_text = panes[i][0];
                link_title = panes[i][1];
            }
            divs[i] = $('<div></div>');
            links[i] = $('<a pane="'+i+'" href="#">'+link_text+'</a>').click(pane_click);
            if (link_title !== undefined) { links[i].attr('title',link_title); }
            $(links_dom).append(links[i]);
            if (i < panes.length-1) { $(links_dom).append(' | '); }
            $(divs_dom).append(divs[i]);
        }

        return {
            'links' : links_dom,
            'panes' : divs_dom,
            'pane' : pane,
            'link' : link,
            'show' : show,
            'current' : current,
            'hide_all' : hide_all
        };
    }

    // Abstraction for handling cutters

    function Cutter_List(enzymes_feature_list) {
        this.enzymes = enzymes_feature_list;
    }

    function __cutter_sorter(a,b) {
        if (a.name() < b.name()) { return -1; }
        if (a.name() > b.name()) { return 1; }
        return 0;
    }

    Cutter_List.prototype.unique=function(){
        if (this.__unique) { return this.__unique; }
        this.__unique = [];
        for (var i = 0; i < this.enzymes.length; i++) {
            if (this.enzymes[i].cut_count() == 1) {
                this.__unique.push(this.enzymes[i]);
            }
        }
        this.__unique.sort(__cutter_sorter);
        return this.__unique;
    };

    Cutter_List.prototype.all=function(){
        if (this.__all) { return this.__all; }
        this.__all = [];
        var check = {};
        for (var i = 0; i < this.enzymes.length; i++) {
            if (!(this.enzymes[i].name() in check)) {
                this.__all.push(this.enzymes[i]);
                check[this.enzymes[i].name()] = 1;
            }
        }
        this.__all.sort(__cutter_sorter);
        return this.__all; 
    };

    function sequence_tab(dom) {
        var copy_all = 'To copy sequence: click on sequence, hit ctrl/cmd-A, then ctrl/cmd-C';

        panes = Switch_Panes(['FASTA','GenBank','Reverse Complement']);

        $(dom).append('<p>Current sequence: '+sequence.length()+' base pairs</p>')
              .append(panes.links)
              .append(panes.panes);

        $(panes.pane(0))
            .append('<p>'+copy_all+'</p>')
            .append($('<textarea readonly></textarea>')
                        .addClass('giraffe-seq-textarea')
                        .val(BioJS2.fasta(sequence,name,false)));

        var features = [];
        for (var i = 0; i < gd.all_features.length; i++) {
            if (gd.all_features[i].is_enzyme()) { continue; }
            var type = "misc_feature";
            var label = gd.all_features[i].name();
            var gene = "";
            if (gd.all_features[i].type() == gd.Feature_Type.origin) {
                type = "rep_origin";
            }
            else if (gd.all_features[i].type() == gd.Feature_Type.gene) {
                type = "gene";
                gene = gd.all_features[i].name();
            }
            else if (gd.all_features[i].is_orf()) {
                type = "CDS";
            }
            else if (gd.all_features[i].type() == gd.Feature_Type.promoter) {
                type = "promoter";
            }
            else if (gd.all_features[i].type() == gd.Feature_Type.terminator) {
                type = "terminator";
            }
            var f = {
                label : label,
                gene : gene,
                type : type,
                start : gd.all_features[i].start(),
                end : gd.all_features[i].end(),
                clockwise : gd.all_features[i].clockwise(),
                clockwise_sequence : gd.all_features[i].clockwise_sequence()
            };
            features.push(f); 
        }

        $(panes.pane(1))
            .append('<p>'+copy_all+'</p>')
            .append($('<textarea readonly></textarea>')
                        .addClass('giraffe-seq-textarea')
                        .val(BioJS2.genbank(sequence,name,false,features)));

        $(panes.pane(2))
            .append('<p>'+copy_all+'</p>')
            .append($('<textarea readonly></textarea>')
                        .addClass('giraffe-seq-textarea')
                        .val(BioJS2.fasta(sequence.reverse_complement(),name,false)));

        panes.hide_all();
        panes.show(0);
    }

    function map_tab(dom) {
        panes = Switch_Panes(['Circular Map', 'Linear Map']);

        var help, // DOMs
            dom_zoom_id_c = random_dom_id(), 
            dom_map_id_c = random_dom_id(), 
            dom_map_c,
            dom_align_c,
            dom_control_id_c = random_dom_id(), 
            dom_control_c,
            dom_zoom_id_l = random_dom_id(), 
            dom_map_id_l = random_dom_id(), 
            dom_map_l,
            dom_align_l,
            dom_control_id_l = random_dom_id(), 
            dom_control_l,
            gt, gd_c, gd_l, gc_c, gc_l; // GriaffeDraw/Table/Controls

        help =
            $('<p id="giraffe-map-help" '+
              ' class="giraffe-help giraffe-hide '+
                      'ui-widget ui-corner-all ui-widget-content">'+
              'Click on a feature label or feature to highlight DNA sequence. Shift-click to copy sequence.'+
              '</p>');


        $(dom)
            .append(help)
            .append(panes.links)
            .append(panes.panes);


        // Circular map pane
        dom_zoom_c = $('<a></a>').text('Zoom/Reset').addClass('giraffe-zoom-control').click(function() {
          var zoomable = $('#'+dom_zoom_id_c);
          if ($(zoomable).hasClass('giraffe-zoom')) { $(zoomable).removeClass('giraffe-zoom'); } else { $(zoomable).addClass('giraffe-zoom'); } 
        });
        dom_zoomable_c = $('<div id="'+dom_zoom_id_c+'"></div>');
        dom_map_c = $('<div id="'+dom_map_id_c+'" class="giraffe-analyze-map giraffe-analyze-circular-map"></div>');
        dom_align_c = $('<div class="giraffe-analyze-alignment"></div>');
        dom_control_c = $('<div id="' + dom_control_id_c + '" class="giraffe-analyze-map-control"></div>');
        
        $(dom_zoomable_c).append(dom_zoom_c).append(dom_map_c);
        $(panes.pane(0))
            .append(dom_zoomable_c)
            .append(dom_align_c)
            .append(dom_control_c);

        gd_c = gd.CircularMap({
            'map_dom_id' : dom_map_id_c,
            'plasmid_name' : name,
            'cutters': [1],
            'map_width' : map_width,
            'map_height' : map_height,
            'feature_click_callback' : map_feature_click_callback
        });
        gc_c = GiraffeControl($, gd_c, dom_control_c, gd, 'map_gd_c', exclude_layers);

        // Linear map pane
        dom_zoom_l = $('<a></a>').text('Zoom/Reset').addClass('giraffe-zoom-control').click(function() {
          var zoomable = $('#'+dom_zoom_id_l);
          if ($(zoomable).hasClass('giraffe-zoom')) { $(zoomable).removeClass('giraffe-zoom'); } else { $(zoomable).addClass('giraffe-zoom'); } 
        });
        dom_zoomable_l = $('<div id="'+dom_zoom_id_l+'"></div>');
        dom_map_l = $('<div id="'+dom_map_id_l+'" class="giraffe-analyze-map giraffe-analyze-linear-map"></div>');
        dom_align_l = $('<div class="giraffe-analyze-alignment"></div>');
        dom_control_l = $('<div id="' + dom_control_id_c + '" class="giraffe-analyze-map-control"></div>');

        $(dom_zoomable_l).append(dom_zoom_l).append(dom_map_l);
        $(panes.pane(1))
            .append(dom_zoomable_l)
            .append(dom_align_l)
            .append(dom_control_l);

        gd_l = gd.LinearMap({
            'map_dom_id' : dom_map_id_l,
            'plasmid_name' : name,
            'cutters': [1],
            'map_width' : map_width,
            'map_height' : map_height,
            'feature_click_callback' : map_feature_click_callback
        });
        gc_l = GiraffeControl($, gd_l, dom_control_l, gd, 'map_gd_l', exclude_layers);

        panes.hide_all();
        if (starts_with_linear_map) { panes.show(1); }
        else { panes.show(0); }

        $('svg path, svg text').mouseover(function(){ $(help).show(); });
        $('svg path, svg text').mouseout(function(){ $(help).hide(); });

        sequence_viewer_bp_event(dom);
    }

    function digest_tab(dom) {

        var map_objects = new Array(2);

        function digest_map_panes(dom) {

            var cpanes,
                dom_map_c,
                dom_map_id_c = random_dom_id(),
                dom_align_c,
                dom_control_c,
                dom_map_l,
                dom_map_id_l = random_dom_id(),
                dom_align_l,
                dom_control_l,
                circular_digest_map_shrink_factor = 1;

            // Cutter map above
            cpanes = Switch_Panes(['Linear Digest', 'Circular Digest']);

            $(dom)
                .append(cpanes.panes);

            // Linear digest pane
            dom_map_l = $('<div id="'+ dom_map_id_l+'" class="giraffe-analyze-map giraffe-analyze-linear-map giraffe-digest-map"></div>');
            dom_align_l = $('<div class="giraffe-analyze-alignment"></div>');
            dom_control_l = $('<div id="' + random_dom_id()  + '" class="giraffe-analyze-map-control giraffe-digest-control"></div>');
            $(cpanes.pane(0))
                .append(dom_map_l)
                .append(dom_align_l)
                .append(dom_control_l);

            gd_l = gd.LinearMap({
                'map_dom_id' : dom_map_id_l,
                'plasmid_name' : name,
                'digest' : true,
                'cutters': [1],
                'map_width' : map_width,
                'map_height' : map_height,
                'feature_click_callback' : map_feature_click_callback
            });
            gc_l = GiraffeControl($, gd_l, dom_control_l, gd, "digest_gd_c", exclude_layers);
            map_objects[0] = gd_l;

            // Circular digest pane
            dom_map_c = $('<div id="'+ dom_map_id_c+'" class="giraffe-analyze-map giraffe-analyze-circular-map giraffe-digest-map"></div>');
            dom_align_c = $('<div class="giraffe-analyze-alignment"></div>');
            dom_control_c = $('<div id="' + random_dom_id()  + '" class="giraffe-analyze-map-control giraffe-digest-control"></div>');
            $(cpanes.pane(1))
                .append(dom_map_c)
                .append(dom_align_c)
                .append(dom_control_c);

            gd_c = gd.CircularMap({
                'map_dom_id' : dom_map_id_c,
                'plasmid_name' : name,
                'digest' : true,
                'cutters': [1],
                'map_width' : map_width * circular_digest_map_shrink_factor,
                'map_height' : map_height * circular_digest_map_shrink_factor,
                'feature_click_callback' : map_feature_click_callback
            });
            gc_c = GiraffeControl($, gd_c, dom_control_c, gd, "digest_gd_c", exclude_layers);
            map_objects[1] = gd_c;

            // Show the linear map by default
            cpanes.hide_all();
            cpanes.show(0);

            return cpanes;
        }

        // Labels at the top
        var label_panes = Switch_Panes(
            [['Cutters','See restriction enzymes that cut the sequence'],
             ['Linear Digest','See restriction digest bands assuming a linear sequence'],
             ['Circular Digest','See restriction digest bands assuming a circular sequence']
            ]
        );

        $(dom)
            .append(label_panes.links);

        // Digest data below
        var digest = Switch_Panes(
            ['Cutters', 'Linear Digest', 'Circular Digest']
        );

        // Digest maps above: need to pass in digest panes so that
        // the map controls can pick the corresponding digest pane
        var map_panes = digest_map_panes(dom);
        var cutters_to_show = [1];

        var digest_data_dom = 
            $('<div id="giraffe-digest-data"></div>')
                .appendTo(dom);

        // Make this function using closures, so that the function
        // definitions and generic cutter lists get read only once--not each
        // time this function is called
        var write_digest_data = (function () {
            var list;
            var all = cutters.all();

            function make_cutter_list() {
                var c, i;
                var all_of_this, cuts, fids;
                var name, s, item;

                if (typeof(cutters_to_show) == 'undefined' || cutters_to_show.length > 0) {
                    for (i = 0; i < all.length; i++) {
                        all_of_this = all[i].other_cutters();
                        cuts = [];
                        fids = [];
                        for (c = 0; c < all_of_this.length; c++) {
                            cuts.push(gd.all_features[all_of_this[c]].cut());
                            fids.push(gd.all_features[all_of_this[c]].id());
                        }
                        if (typeof(cutters_to_show) == 'undefined' ||
                            cutters_to_show.indexOf(cuts.length) >= 0) {
                            name = $('<td></td>')
                                    .addClass('enzyme-label')
                                    .append(all[i].name());
                            for (c = 0; c < cuts.length; c++) {
                                cuts[c] = '<a href="#" seq-title="'+all[i].name() +
                                    ' cut site" bp="feature-'+fids[c]+'" class="giraffe-bp">'+cuts[c]+'</a>';
                            }
                            s = $('<td>Cuts after '+cuts.join(', ')+'</td>');
                            item = $('<tr></tr>').append(name).append(s);
                            $(list).append(item);
                        }
                    }
                }
            }

            function make_digest_list(circular) {
                var a0;

                function cutter_sort(a,b) {
                    return gd.all_features[a].start() - gd.all_features[b].start();
                }

                if (typeof(cutters_to_show) == 'undefined' ||
                    cutters_to_show.length > 0) {
                    for (var i = 0; i < all.length; i++) {
                        var cuts = [];
                        var all_of_this = all[i].other_cutters();
                        all_of_this.sort(cutter_sort);
                        for (var c = 0; c < all_of_this.length; c++) {
                            cuts.push(gd.all_features[all_of_this[c]].cut());
                        }

                        if (typeof(cutters_to_show) == 'undefined' ||
                            cutters_to_show.indexOf(cuts.length) >= 0) {
                            var name = $('<td></td>')
                                        .addClass('enzyme-label')
                                        .append(all[i].name());
                            var digests = [];
                            for (var j=0; j<cuts.length; j++) {
                                if (j === 0 && !circular) {
                                    a0 = '<a href="#" class="giraffe-bp" ' +
                                        'seq-title="Fragment cut by ' +
                                        all[i].name() + '" bp="1,'+cuts[j]+'">';
                                    digests.push(a0+'1-'+(cuts[j])+'</a>&nbsp;('+cuts[j]+'&nbsp;bp)');
                                }
                                if (j+1 == cuts.length) {
                                    if (circular) {
                                        a0 = '<a href="#" class="giraffe-bp" ' +
                                            'seq-title="Fragment cut by ' + 
                                            all[i].name()+'" bp="' +
                                            (cuts[j]+1)+','+cuts[0]+'">';
                                        digests.push(a0+(cuts[j]+1)+'-'+cuts[0]+'</a>&nbsp;('+
                                                     (seqlen-(cuts[j]+1)+1+cuts[0])+'&nbsp;bp)');
                                    } else {
                                        a0 = '<a href="#" class="giraffe-bp" ' +
                                            'seq-title="Fragment cut by ' +
                                            all[i].name()+'" bp="' +
                                            (cuts[j]+1)+','+seqlen+'">';
                                        digests.push(a0+(cuts[j]+1)+'-'+seqlen+'</a>&nbsp;('+
                                                     (seqlen-(cuts[j]+1)+1)+'&nbsp;bp)');
                                    }
                                } else {
                                    a0 = '<a href="#" class="giraffe-bp" ' +
                                        'seq-title="Fragment cut by ' +
                                        all[i].name()+'" bp="' +
                                        (cuts[j]+1)+','+cuts[j+1]+'">';
                                    digests.push(a0+(cuts[j]+1)+'-'+(cuts[j+1])+'</a>&nbsp;('+
                                                 (cuts[j+1]-(cuts[j]+1)+1)+'&nbsp;bp)');
                                }
                            }
                            var s = $('<td>'+digests.join(', ')+'</td>');
                            var item = $('<tr></tr>').append(name).append(s);
                            $(list).append(item);
                        }
                    }
                }
            }

            // The actual digest drawing function
            return function () {
                var whole_table;
                digest_data_dom.empty();
                whole_table = $('<table></table>')
                    .append('<colgroup>' +
                                '<col class="enzyme-label" />' +
                                '<col class="enzyme-content" />' +
                            '</colgroup>')
                    .append('<tbody></tbody>')
                    .addClass('giraffe-enzyme-list');

                list = whole_table.find('tbody');

                switch (label_panes.current()) {
                    case 0:
                        make_cutter_list();
                        break;
                    case 1:
                        make_digest_list(false);
                        break;
                    case 2:
                        make_digest_list(true);
                        break;
                    default:
                        break;
                }

                digest_data_dom.append(whole_table);
                sequence_viewer_bp_event(digest_data_dom);
            };
        })();

        $(label_panes.links).click(function (event) {
            var pane;

            // Pick which map to draw, depending on the
            // tab that's clicked
            switch (label_panes.current()) {
                case 0:
                case 1:
                    pane = 0;
                    break;
                case 2:
                    pane = 1;
                    break;
                default:
                    pane = 0;
                    break;
            }
            
            // Show the appropriate pane
            map_panes.show(pane);

            // Update cutters_to_show to reflect the checkboxes selected in that pane
            cutters_to_show = [];
            $(map_panes.pane(pane)).find(":checked").each(function () {
                if ($(this).attr('name')) {
                    cutters_to_show.push(parseInt($(this).attr('name').match(/\d+/), 10));
                }
            });
            
            if ($(map_panes.pane(pane)).find('input.all-cutters').is(":checked")) {
                cutters_to_show = undefined;
            }

            // Redraw the digest
            write_digest_data();
        });

        // Add an "all cutters" checkbox
        $(map_panes.panes)
            .find('input[name="cutters-2"]')
            .closest('td')
            .after('<td><label><input class="all-cutters" type="checkbox" name="all-cutters" value="show" />' +
                   '<span class="cutter-label">All</span></label></td>');
                          

        // Force rewriting the digest data when the cutter controls are changed
        $(map_panes.panes)
            .find('input[name*="cutters"]')
            .not('[name="all-cutters"]')
            .click(function (event) {
                var map = $(this).closest('div.giraffe-digest-control').siblings('div.giraffe-digest-map'),
                    n_cutter_boxes;

                cutters_to_show = [];

                // Parse out selected options
                n_cutter_boxes = 0;
                $(this).closest('tbody').find('input[name|="cutters"]').each(function () {
                    n_cutter_boxes++;
                    if ($(this).is(':checked')) {
                        cutters_to_show.push(
                            parseInt($(this).attr('name').match(/\d+/), 10)
                        );
                    }
                });

                // Make sure all-cutters checkbox is unchecked if the list is
                // not at maximum capacity
                if (cutters_to_show.length < n_cutter_boxes) {
                    $(this).closest('tbody').find('input[name="all-cutters"]').removeAttr('checked');
                }

                write_digest_data();
            });

        $(map_panes.panes).find('input[name="all-cutters"]').click(function (event) {
            var map = $(this).closest('div.giraffe-digest-control').siblings('div.giraffe-digest-map'),
                n_cutter_boxes;

            if ($(this).is(':checked')) {
                // Make sure 1- and 2- cutter checkboxes are no longer checked
                $(this).closest('tbody').find('input[name|="cutters"]').removeAttr('checked');
                // Show all cutters below
                cutters_to_show = undefined;
                map_objects[map_panes.current()].redraw_cutters(undefined);
                write_digest_data();

            } else {
                cutters_to_show = new Array();
                map_objects[map_panes.current()].redraw_cutters();
                write_digest_data();
            }

        });

        // Select the cutter pane and draw everything the first time
        $(label_panes.link(0)).click();

    }

    function translate_tab(dom) {
        var starts_with, gene_desc;
        var i, j, f, g, f_end, g_end;

        var seq_start, seq_end, title, t;
        var s, p, overlay_switch;

        panes = Switch_Panes(
            ['ORFs',
             "5'3' Frame 1",
             "5'3' Frame 2",
             "5'3' Frame 3",
             "3'5' Frame 1",
             "3'5' Frame 2",
             "3'5' Frame 3"]
        );

        $(dom)
            .append(panes.links)
            .append(panes.panes);

        $(panes.pane(0))
            .append('<p>Click on ORF bp numbers to highlight sequence.</p>');

        starts_with = 1;
        for (i = 0; i < gd.orf_features.length; i++) {
            f = gd.orf_features[i];

            // does this ORF cover, or is the same as, a gene?
            gene_desc = '';
            for (j = 0; j < gd.all_features.length; j++) {
                if (gd.all_features[j].type() == gd.Feature_Type.gene &&
                    gd.all_features[j].clockwise() == f.clockwise()) {
                    g = gd.all_features[j];
                    f_end = f.end();
                    if (f.end() < f.start()) { f_end = f_end+seqlen; }
                    g_end = g.end();
                    if (g.end() < g.start()) { g_end = g_end+seqlen; }
                    if (g.start() >= f.start() && g_end <= f_end) {
                        gene_desc = 'contains '+g.name();
                    }
                    else if (g.start() < f.start() && g_end > f_end) {
                        gene_desc = 'within '+g.name();
                    }
                    else if ((g.start() < f.start() && g_end > f.start()) ||
                             (g.start() < f_end && g_end > f_end)) {
                        gene_desc = 'overlaps with '+g.name();
                    }
                }
            }

            starts_with = 0;
            s = f.clockwise_sequence();

            if (f.clockwise()) {
                s = new BioJS2.DNASequence(s);
                p = s.translate();
                seq_start = f.start();
                seq_end = f.end();
            }
            else {
                s = new BioJS2.DNASequence(s).reverse_complement();
                p = s.translate();
                seq_start = f.end();
                seq_end = f.start();
            }
        
            overlay_switch = Switch_Panes(['AA only', 'With DNA']);
            $(overlay_switch.pane(0)).append(p.format_html_with_bp());
            $(overlay_switch.pane(1)).append(s.format_html_with_aa(seq_start,seq_end));
            overlay_switch.show(0);

            title = 'ORF';
            if (gene_desc !== '') { title += ', '+gene_desc; }
            t = 'ORF <a href="#" class="giraffe-bp" ' +
                'seq-title="'+title+'" bp="' + 
                f.start()+','+f.end()+'">';
            if (f.clockwise()) { t += f.start()+' - '+f.end(); }
            else { t += f.end()+' - '+f.start()+' antisense'; }
            t += '</a> ('+s.length()/3+' aa)';
            if (gene_desc !== '') { t += ', '+gene_desc; }
            if (f.end() < f.start()) {
                t += ' <span class="giraffe-red">ORF based on circular DNA</span>';
            }
            
            title = $('<p></p>').append(t);
            $(title).append(overlay_switch.links);

            $(panes.pane(0))
                .append($('<div></div>').addClass('giraffe-orf-group')
                            .append(title)
                            .append($('<div></div>').addClass('giraffe-seq')
                                                    .addClass('giraffe-left')
                                                    .addClass('giraffe-protein')
                                                    .append(overlay_switch.panes)
                            )
                            .append(
                                $('<div></div>')
                                    .append($(BioJS2.NCBI_blastp_form(p)))
                                    .addClass('giraffe-ncbi-button')
                                    .addClass('giraffe-left')
                                    .addClass('giraffe-left-last')
                            )
                            .append($('<div>&nbsp;</div>').addClass('giraffe-clear'))
                       );
        }

        p = sequence.translate();
        overlay_switch = Switch_Panes(['AA only', 'With DNA']);
        $(overlay_switch.pane(0)).append(p.format_html_with_bp());
        $(overlay_switch.pane(1)).append(sequence.format_html_with_aa());
        overlay_switch.show(0);

        $(panes.pane(1)).append(overlay_switch.links).append(
            $('<div></div>').addClass('giraffe-seq')
                            .addClass('giraffe-left')
                            .addClass('giraffe-protein')
                            .append(overlay_switch.panes)
        ).append(
            $(BioJS2.NCBI_blastp_form(p))
                .addClass('giraffe-left')
                .addClass('giraffe-left-last')
        );

        s = sequence.substring(1);
        p = s.translate();
        overlay_switch = Switch_Panes(['AA only', 'With DNA']);
        $(overlay_switch.pane(0)).append(p.format_html_with_bp());
        $(overlay_switch.pane(1)).append(s.format_html_with_aa(2));
        overlay_switch.show(0);

        $(panes.pane(2)).append(overlay_switch.links).append(
            $('<div></div>').addClass('giraffe-seq')
                            .addClass('giraffe-left')
                            .addClass('giraffe-protein')
                            .append(overlay_switch.panes)
        ).append(
            $(BioJS2.NCBI_blastp_form(p))
                .addClass('giraffe-left')
                .addClass('giraffe-left-last')
        );

        s = sequence.substring(2);
        p = s.translate();
        overlay_switch = Switch_Panes(['AA only', 'With DNA']);
        $(overlay_switch.pane(0)).append(p.format_html_with_bp());
        $(overlay_switch.pane(1)).append(s.format_html_with_aa(3));
        overlay_switch.show(0);

        $(panes.pane(3)).append(overlay_switch.links).append(
            $('<div></div>').addClass('giraffe-seq')
                            .addClass('giraffe-left')
                            .addClass('giraffe-protein')
                            .append(overlay_switch.panes)
        ).append(
            $(BioJS2.NCBI_blastp_form(p))
                .addClass('giraffe-left')
                .addClass('giraffe-left-last')
        );

        s = sequence.reverse_complement();
        p = s.translate();
        overlay_switch = Switch_Panes(['AA only', 'With DNA']);
        $(overlay_switch.pane(0)).append(p.format_html_with_bp());
        $(overlay_switch.pane(1)).append(s.format_html_with_aa(sequence.length(),1));
        overlay_switch.show(0);

        $(panes.pane(4)).append(overlay_switch.links).append(
            $('<div></div>').addClass('giraffe-seq')
                            .addClass('giraffe-left')
                            .addClass('giraffe-protein')
                            .append(overlay_switch.panes)
        ).append(
            $(BioJS2.NCBI_blastp_form(p))
                .addClass('giraffe-left')
                .addClass('giraffe-left-last')
        );
        
        s = sequence.reverse_complement().substring(1);
        p = s.translate();
        overlay_switch = Switch_Panes(['AA only', 'With DNA']);
        $(overlay_switch.pane(0)).append(p.format_html_with_bp());
        $(overlay_switch.pane(1)).append(s.format_html_with_aa(sequence.length()-1,1));
        overlay_switch.show(0);

        $(panes.pane(5)).append(overlay_switch.links).append(
            $('<div></div>').addClass('giraffe-seq')
                            .addClass('giraffe-left')
                            .addClass('giraffe-protein')
                            .append(overlay_switch.panes)
        ).append(
            $(BioJS2.NCBI_blastp_form(p))
                .addClass('giraffe-left')
                .addClass('giraffe-left-last')
        );

        s = sequence.reverse_complement().substring(2);
        p = s.translate();
        overlay_switch = Switch_Panes(['AA only', 'With DNA']);
        $(overlay_switch.pane(0)).append(p.format_html_with_bp());
        $(overlay_switch.pane(1)).append(s.format_html_with_aa(sequence.length()-2,1));
        overlay_switch.show(0);

        $(panes.pane(6)).append(overlay_switch.links).append(
            $('<div></div>').addClass('giraffe-seq')
                            .addClass('giraffe-left')
                            .addClass('giraffe-protein')
                            .append(overlay_switch.panes)
        ).append(
            $(BioJS2.NCBI_blastp_form(p))
                .addClass('giraffe-left')
                .addClass('giraffe-left-last')
        );

        panes.hide_all();
        panes.show(starts_with);
    }

    function blast_tab(dom) {
        $(dom).append('<p><b>BLAST</b></p>'+
            '<p>BLAST finds regions of similarity between biological sequences. Click on the buttons below to BLAST your sequence. Results will appear in a new window.</p>');
        var blastn = $(BioJS2.NCBI_blastn_form(sequence));
        var blastx = $(BioJS2.NCBI_blastx_form(sequence));
        $(dom).append('<p>Search for matching nucleotide sequence with BLASTN:</p>')
            .append(blastn);
        $(dom).append('<p>Search for matching protein sequence with BLASTX:</p>')
            .append(blastx);
        var recent = $(BioJS2.NCBI_recent_results_link());
        $(recent).append('See recent BLAST results on NCBI website.');
        $(dom).append($('<p></p>').append(recent));
    }

    function align_tab(dom) {
        $(dom).append('<p><b>Align Sequence with BLAST2</b></p>'+
            "<p>NCBI's BLAST2 program aligns two sequences. Enter a new sequence to align against your sequence. Results will appear in a new window.</p>");
        var blast2 = $(BioJS2.NCBI_blast2_form(sequence)).addClass('giraffe-blast2')
                .append('<input type="reset" name="reset" value="Clear"/>');
        $(dom).append(blast2);
        var recent = $(BioJS2.NCBI_recent_results_link());
        $(recent).append('See recent BLAST results on NCBI website.');
        $(dom).append($('<p></p>').append(recent));
    }

    // Set of tabs for analyzing the sequence, but does not include
    // the sequence viewer.
    function analyzer_tabs(dom) {
        // Create each tab
        var dom_id_sequence = random_dom_id();
        var dom_tab_sequence = $('<div id="'+dom_id_sequence+'"></div>')
            .addClass('giraffe-tab');
        var dom_id_map = random_dom_id();
        var dom_tab_map = $('<div id="'+dom_id_map+'"></div>')
            .addClass('giraffe-tab');
        var dom_id_blast = random_dom_id();
        var dom_tab_blast = $('<div id="'+dom_id_blast+'"></div>')
            .addClass('giraffe-tab');
        var dom_id_align = random_dom_id();
        var dom_tab_align = $('<div id="'+dom_id_align+'"></div>')
            .addClass('giraffe-tab');
        var dom_id_digest = random_dom_id();
        var dom_tab_digest = $('<div id="'+dom_id_digest+'"></div>')
            .addClass('giraffe-tab');
        var dom_id_translate = random_dom_id();
        var dom_tab_translate = $('<div id="'+dom_id_translate+'"></div>')
            .addClass('giraffe-tab');
        // Main tab bar
        var dom_tabs = $('<div></div>').append(
            '<ul>'+
            '<li><a href="#'+dom_id_map+'">Map and Features</a></li>'+
            '<li><a href="#'+dom_id_sequence+'">Sequence</a></li>'+
            '<li><a href="#'+dom_id_blast+'">Blast</a></li>'+
            '<li><a href="#'+dom_id_align+'">Align</a></li>'+
            '<li><a href="#'+dom_id_digest+'">Digest</a></li>'+
            '<li><a href="#'+dom_id_translate+'">Translate</a></li>'+
            '</ul>'
        ).append(dom_tab_map)
         .append(dom_tab_sequence)
         .append(dom_tab_blast)
         .append(dom_tab_align)
         .append(dom_tab_digest)
         .append(dom_tab_translate)
         .append($('<div></div>').addClass('giraffe-clear'))
         .addClass('giraffe-tabs');

        $(dom).append(dom_tabs);
        $(dom_tabs).tabs();

        map_tab(dom_tab_map);
        sequence_tab(dom_tab_sequence);
        digest_tab(dom_tab_digest);
        translate_tab(dom_tab_translate);
        blast_tab(dom_tab_blast);
        align_tab(dom_tab_align);
    }

    // Sequence viewer

    var sequence_viewer_topbar_highlight;
    var sequence_viewer_topbar_mouseover;
    var search_rc = false;
    var search_next = -1;

    function sequence_viewer(dom) {
        var viewer = $('<div></div>').addClass('giraffe-viewer');

        var sequence_viewer_search = $('<div></div>')
            .attr('id', 'giraffe-viewer-search-container')
            .append($('<textarea></textarea>')
                        .attr('id', 'giraffe-viewer-search-textarea'))
            .append($('<input type="submit" value="Search">')
                        .attr('id', 'giraffe-viewer-search-button'));

        sequence_viewer_topbar_highlight = $('<div></div>')
            .attr('id', 'giraffe-viewer-topbar-highlight');
        sequence_viewer_topbar_mouseover = $('<div></div>')
            .attr('id', 'giraffe-viewer-topbar-mouseover');

        var topbar = $('<div></div>').addClass('giraffe-viewer-topbar')
            .append(sequence_viewer_search)
            .append(sequence_viewer_topbar_highlight)
            .append(sequence_viewer_topbar_mouseover)
            .append('&nbsp;');

        // Sequence viewer is basically a table, each cell has 10 bps.
        var seq_viewer = $('<div></div>').addClass('giraffe-seq-viewer');
        var table = $('<table></table>');
        $(seq_viewer).append(table);

        var row;
        var start;
        var end;
        var lines_10 = BioJS2.wrap(sequence.sequence(),10);
        function seq_mouseenter() {
            $(this).addClass('giraffe-seq-mouseover');
            var title = $(this).attr('start')+'-'+$(this).attr('end');
            $(sequence_viewer_topbar_mouseover).html(title);
        }
        function seq_mouseleave() {
            $(this).removeClass('giraffe-seq-mouseover');
            $(sequence_viewer_topbar_mouseover).html("");
        }
    
        for (var i=0,j=0; i<lines_10.length; i++) {
            if (j === 0) {
                row = $('<tr></tr>');
                $(table).append(row);
                start = i*10+1;
                $(row).append
                    ('<td class="giraffe-bp-marker giraffe-bp-marker-left">'+start+'</td>');
            }
            start = i*10+1;
            end = (i+1)*10;
            var td = $('<td></td>')
                .attr('id','giraffe-bp-'+start)
                .attr('start',start)
                .attr('end',end)
                .mouseenter(seq_mouseenter)
                .mouseleave(seq_mouseleave)
                .append(lines_10[i]);
            $(row).append(td);
            j++;
            if (j == viewer_segs_per_line && i+1 < lines_10.length) {
                j = 0;
                end = (i+1)*10;
                $(row).append
                    ('<td class="giraffe-bp-marker giraffe-bp-marker-right">'+end+'</td>');
            }
            if (i+1 == lines_10.length) {
                $(row).append
                    ('<td class="giraffe-bp-marker giraffe-bp-marker-right">' +
                     sequence.length()+'</td>');
            }
        }

        // messages for search, normally hidden
        var search_not_found = $('<div></div>')
            .attr('id','giraffe-viewer-search-not-found')
            .append('Search: cannot find sequence')
            .attr('title', 'Sequence Search')
            .hide();

        $(viewer)
            .append(topbar)
            .append(seq_viewer)
            .append(search_not_found);

        $(dom).append(viewer);

        // for searching:
        var rc = sequence.reverse_complement();

        $('#giraffe-viewer-search-textarea').change(function(){
            search_next = -1;
            search_rc = false;
        });
        $('#giraffe-viewer-search-button').click(function(){
            var q = $('#giraffe-viewer-search-textarea').val();
            q = q.replace(/\s/g,'');
            $('#giraffe-viewer-search-textarea').val(q);
            var n;
            var search_last = search_next;
            if (!search_rc) {
                n = sequence.find(q,search_next);
                if (n == -1) {
                    search_next = -1;
                    search_rc = true;
                    n = rc.find(q,search_next);
                }
            }
            else { n = rc.find(q,search_next); }

            /* handles wrapping around from end of search */
            if (n == -1 && search_last != -1) {
                search_rc = false;
                n = sequence.find(q,-1);
                if (n == -1) {
                    search_rc = true;
                    n = rc.find(q,-1);
                }
            }

            if (n == -1) {
                $(search_not_found).dialog({
                    modal: true,
                    position: 'top',
                    buttons: { 'Close' : function() { $(this).dialog( "close" ); } }
                });
                search_next = -1;
                search_rc = true;
            }
            else {
                search_next = n+q.length;
                sequence_viewer_clear_highlight();
                var bp;
                if (search_rc) {
                    bp = [sequence.length()-(n+q.length-1)+1,sequence.length()-n+1];
                    sequence_viewer_bp_event_highlight(bp,'Reverse complement of query');
                }
                else {
                    bp = [n,n+q.length-1];
                    sequence_viewer_bp_event_highlight(bp,'Query');
                }
            }
        });
    }

    // global list of td's that have span in the middle
    var global_has_span_td = [];

    function sequence_viewer_clear_highlight() {
        $(sequence_viewer_topbar_highlight).html("");
        $('.giraffe-seq-highlight').removeClass('giraffe-seq-highlight');
        $('.giraffe-bp-click-source').removeClass('giraffe-bp-click-source');
        for (i = 0; i < global_has_span_td.length; i++) {
            var t = $(global_has_span_td[i]).text();
            t = t.replace(/\s/g,'');
            $(global_has_span_td[i]).html(t);
        }
        global_has_span_td = [];
    }

    function sequence_viewer_bp_event(selection) {
        $(selection).find('.giraffe-bp').click(function(evt){
            var bpstr, title, bp, 
                fid, feature;

            sequence_viewer_clear_highlight();
            $(this).addClass('giraffe-bp-click-source');
            evt.preventDefault();

            bpstr = $(this).attr('bp');

            // Check for feature-style or range-style bp-data
            if (bpstr.indexOf('feature-') === 0) {
                fid = parseInt(bpstr.replace(/\D/g, ''), 10);
                feature = gd.all_features[fid];

                // Fancy highlight that shows cut sites for enzymes
                map_feature_click_callback(feature);
            } else {
                title = $(this).attr('seq-title');
                bp = bpstr.split(',');

                if (bp.length > 0) { 
                    sequence_viewer_bp_event_highlight(bp,title); 
                }
            }
        });
    }

    function sequence_viewer_bp_event_highlight(bp,title,link) {
        var i;
        var t, new_t;

        for (i = 0; i < bp.length; i++) { bp[i] = parseInt(bp[i], 10); }
        // find start bp position for the first td
        var first_td = Math.floor((bp[0]-1)/10)*10+1;
        // find start bp position of the last td
        var last_td = first_td;
        if (bp.length > 1) {
            last_td = Math.floor((bp[1]-1)/10)*10+1;
        }
        else { bp[1] = bp[0]; }
        
        var desc = bp[0];
        if (bp[0] != bp[1]) { desc += '-'+bp[1]; }
        if (link) {
            desc += ': <a href="'+link+'">'+title+'</a>';
        }
        else {
            desc += ': '+title;
        }
        $(sequence_viewer_topbar_highlight).html(desc);

        // draw first
        var first_td_dom = $('#giraffe-bp-'+first_td);
        t = $(first_td_dom).text();
        t = t.replace(/\s/g,'');
        
        var span_starts_at, span_ends_before;
        var span0_starts_at, span0_ends_before;
        var span1_starts_at, span1_ends_before;

        if (first_td == last_td && bp[0]>bp[1]) {
            // yikes... difficult, need to draw two spans
            span0_starts_at = 0;
            span0_ends_before = bp[1]+1-first_td;
            span1_starts_at = bp[0]-first_td;
            span1_ends_before = 10;
            new_t = '';
            for (i=0; i<t.length; i++) {
                if (i == span0_starts_at || i == span1_starts_at) {
                    new_t += '<span class="giraffe-seq-highlight">';
                }
                new_t += t.charAt(i);
                if (i == span0_ends_before-1 || i == span1_ends_before-1) {
                    new_t += '</span>';
                }
            }
            $(first_td_dom).html(new_t);
            global_has_span_td.push(first_td_dom);
        }
        else {
            span_starts_at = bp[0]-first_td;
            span_ends_before = 10;
            if (last_td == first_td && bp[0] <= bp[1]) {
                span_ends_before = bp[1]+1-first_td;
            }
            new_t = '';
            for (i=0; i<t.length; i++) {
                if (i == span_starts_at) {
                    new_t += '<span class="giraffe-seq-highlight">';
                }
                new_t += t.charAt(i);
                if (i == span_ends_before-1) {
                    new_t += '</span>';
                }
            }
            $(first_td_dom).html(new_t);
            global_has_span_td.push(first_td_dom);
        }

        // draw everything in between
        var td;

        if (first_td <= last_td && bp[0] <= bp[1]) {
            for (td=first_td+10; td<last_td; td+=10) {
                $('#giraffe-bp-'+td).addClass('giraffe-seq-highlight');
            }
        }
        else {
            var end_td = Math.floor((seqlen-1)/10)*10+1;
            for (td=first_td+10; td<=end_td; td+= 10) {
                $('#giraffe-bp-'+td).addClass('giraffe-seq-highlight');
            }
            for (td=1; td<last_td; td+=10) {
                $('#giraffe-bp-'+td).addClass('giraffe-seq-highlight');
            }
        }

        // draw last
        if (first_td != last_td) {
            if (bp[1] == last_td+10-1) {
                $('#giraffe-bp-'+last_td).addClass('giraffe-seq-highlight');
            }
            else {
                var last_td_dom = $('#giraffe-bp-'+last_td);
                t = $(last_td_dom).text();
                t = t.replace(/\s/g,'');
                span_starts_at = 0;
                span_ends_before = bp[1]-last_td+1;
                new_t = '';
                for (i=0; i<t.length; i++) {
                    if (i == span_starts_at) {
                        new_t += '<span class="giraffe-seq-highlight">';
                    }
                    new_t += t.charAt(i);
                    if (i == span_ends_before-1) {
                        new_t += '</span>';
                    }
                }
                $(last_td_dom).html(new_t);
                global_has_span_td.push(last_td_dom);
            }
        }

        // for best visual, we want to scroll to the first td

        var first_td_line = Math.floor(first_td/(viewer_segs_per_line*10));
        // we want the line to scroll to to not be the first line on
        // screen, but a few lines down
        if (first_td_line > 3) { first_td_line -= 3; }
        var total_lines = Math.floor(seqlen/(viewer_segs_per_line*10))+1;
        var table = $('.giraffe-seq-viewer table');
        var scroll = Math.floor((first_td_line/total_lines)*$(table).height());
        $('.giraffe-seq-viewer').scrollTop(scroll);
    }

    function show_alignment(feature) {
      $('.giraffe-analyze-alignment').empty();
      if (feature.alignment() &&
          feature.alignment().query &&
          feature.alignment().match &&
          feature.alignment().subject) {
        if (feature.alignment().match.indexOf(' ') >= 0) {
          $('<p><b>'+feature.name()+'</b></p>').appendTo('.giraffe-analyze-alignment');
          var alignments = $('<div></div>');
          var al = feature.alignment();
          for (var i=0; i<al.query.length; i++) {
            var q = al.query[i];
            var m = al.match[i];
            if (m == '|') { m = ''; }
            else { m = 'x'; }
            var s = al.subject[i];
            var a = $('<div class="giraffe-alignment-one giraffe-aligned'+m+'"></div>');
            $(a).append(q+'<br/>'+s);
            $(alignments).append(a);
          }
          $('.giraffe-analyze-alignment').append(alignments);
        }
        else {
          $('<p><b>'+feature.name()+'</b>: perfect alignment</p>').appendTo('.giraffe-analyze-alignment');
        }
      }
    }

    function map_feature_click_callback(feature, evt) {
        var bp; // Start and end of feature
        var name = feature.name(); // Tag to display

        sequence_viewer_clear_highlight();
        bp = [feature.start(),feature.end()];

        // Mark cut site if it's an enzyme
        if (feature.type() == gd.Feature_Type.enzyme) {
            if (feature.elucidate()) {
                name += ' (' + feature.elucidate() + ')';
            }
        }

        sequence_viewer_bp_event_highlight(bp,name,feature.link());
        show_alignment(feature);
        if (evt.shiftKey) {
          var selected_seq = sequence.substring(bp[0]-1, bp[1]-1+1);
          prompt("Use Ctrl/Cmd-C to copy the following sequence:", selected_seq.sequence());
        }
    }

    function full_widget() {
        var dom_table = $('<table></table>');
        var dom_row = $('<tr></tr>');
        $(dom_table).append(dom_row);

        var dom_id_viewer = random_dom_id();
        var dom_id_tabs = random_dom_id();

        var dom_viewer = $('<td id="'+dom_id_viewer+'"></td>');
        var dom_tabs = $('<td id="'+dom_id_tabs+'"></td>');

        $(dom_row)
            .append(dom_viewer)
            .append(dom_tabs)
            .append($('<div></div>').addClass('giraffe-clear'));

        var dom_main = $('#'+dom_id);
        $(dom_main).addClass('giraffe-main')
            .append(dom_table);

        sequence_viewer(dom_viewer);
        analyzer_tabs(dom_tabs);
        sequence_viewer_bp_event(dom_viewer);

        $(dom_viewer).addClass('giraffe-viewer-container')
        $(dom_tabs).addClass('giraffe-tabs-container')
        $(dom_main).tooltip();
    }

    full_widget();

};

// Private utility function with no external or closure use
function title_case(str) {
    str = str.replace(/\W/, ' ');
    return str.charAt(0).toUpperCase() + str.slice(1);
}

// Private utility function with no external or closure use
function type_code_to_name(code, gd) {
    // Iterate over the MEMBERS of gd.Feature_Type: NOT AN ARRAY
    for (var type in gd.Feature_Type) {
        if (code == gd.Feature_Type[type]) {
            return title_case(type);
        }
    }

    return "";
}

window.GiraffeTable = function ($,gd,dom) { 
    var enzyme_table,
        feature_table,
        orf_table,
        fx, f,
        row;

    // Read the features in for each table, only displaying the table
    // if there are features for it

    // Standard features
    if (gd.std_features.length > 0) {
        
        // Initialize table
        feature_table = $('<table></table>')
            .append('<colgroup>' +
                        '<col class="giraffe-table-feature-name" />' +
                        '<col class="giraffe-table-feature-data" span="2"/>' +
                    '</colgroup>')
            .append('<thead><tr>' +
                        '<th>Feature Name</th>' +
                        '<th>Start</th>' +
                        '<th>End<th>' +
                    '</tr></thead>')
            .append('<tbody></tbody>')
            .addClass('giraffe-table-feature');

        for (fx = 0; fx < gd.std_features.length; fx++) {
            f = gd.std_features[fx];
            row = $('<tr></tr>').appendTo(feature_table.children('tbody'))
                                    .attr('id', 'feature-' + f.id());

            row.append('<td class="giraffe-table-feature-name">' + f.name() + '</td>');

            if (f.clockwise()) {
                row.append('<td>' + f.start() + '</td>');
                row.append('<td>' + f.end() + '</td>');
            } else {
                row.append('<td>' + f.end() + '</td>');
                row.append('<td>' + f.start() + '</td>');
            }
        }

        $(dom).append(feature_table);
    }

    // ORFs
    if (gd.orf_features.length > 0) {

        // Initialize table
        orf_table = $('<table></table>')
            .append('<colgroup>' +
                        '<col class="giraffe-table-feature-name" />' +
                        '<col class="giraffe-table-feature-data" span="2"/>' +
                    '</colgroup>')
            .append('<thead><tr>' +
                        '<th>ORF</th>' +
                        '<th>Start</th>'     +
                        '<th>End<th>'        +
                    '</tr></thead>')
            .append('<tbody></tbody>')
            .addClass('giraffe-table-orf');

        for (fx = 0; fx < gd.orf_features.length; fx++) {
            f = gd.orf_features[fx];
            row = $('<tr></tr>').appendTo(orf_table.children('tbody'))
                                .attr('id', 'feature-' + f.id());

            row.append('<td class="giraffe-table-feature-name">' + f.name() + '</td>');

            if (f.clockwise()) {
                row.append('<td>' + f.start() + '</td>');
                row.append('<td>' + f.end() + '</td>');
            } else {
                row.append('<td>' + f.end() + '</td>');
                row.append('<td>' + f.start() + '</td>');
            }
        }

        $(dom).append(orf_table);
    }

    // Enzymes
    if (gd.enzyme_features.length > 0) {
        enzyme_table = $('<table></table>')
            .append('<colgroup>' +
                        '<col class="giraffe-table-feature-name" />' +
                        '<col class="giraffe-table-feature-data" />' +
                    '</colgroup>')
            .append('<thead><tr>' +
                        '<th>Enzyme Name</th>' +
                        '<th>Cut</th>' +
                    '</tr></thead>')
            .append('<tbody></tbody>')
            .addClass('giraffe-table-enzyme');

        for (fx = 0; fx < gd.enzyme_features.length; fx++) {
            f = gd.enzyme_features[fx];

            if (f.default_show_feature() && f.cut_count() == 1) {
                row = $('<tr></tr>').appendTo(enzyme_table.children('tbody'))
                                    .attr('id', 'feature-' + f.id());

                row.append('<td class="giraffe-table-feature-name">' + f.name() + '</td>');
                row.append('<td>' + f.cut() + '</td>');
            }
        }

        $(dom).append(enzyme_table);
    }

    // Set general appearance properties
    $(dom).children().addClass('giraffe-table');
    
    return $(dom);
};

window.GiraffeControl = function ($,gd_map,dom,gd,control_name,exclude_layers) {
    var controls,
        table,
        _debug = false,
        draw_enzyme_controls,
        draw_layer_controls,
        num_explicit_cutters,
        control_feat_types,
        feat_control_table,
        ftx, ft;

    draw_enzyme_controls = true;
    draw_layer_controls = true;

    controls = $('<form action="" class="giraffe-controls">' +
        '<fieldset><legend>Feature Options</legend>'+
                   '<table><tbody class="giraffe-controls-layout"></tbody></table>' +
        '</fieldset></form>');

    if (draw_enzyme_controls) {
        controls.find('tbody').append(
            '<tr><td class="enzymes"><table>' +
            '<tbody>' +
                '<tr><th>Restriction Enzymes</th>' +
                '<td><label><input type="checkbox" checked="checked" class="'+control_name+'" name="cutters-1" value="show" />' +
                '<span class="cutter-label">Unique</span></label></td>' +
                '<td><label><input type="checkbox" class="'+control_name+'" name="cutters-2" value="show" />' +
                '<span class="cutter-label">2-cutters</span></label></td>' +
                '</tr>'+
            '</tbody>' +
            '</table></td></tr>');

        num_explicit_cutters = 2;

        // Changes to the Restriction Enzyme selection
        // 1- and 2- cutter checkboxes
        controls.find('input[name|="cutters"]').click(function (event) {
            var opts = [];
            // Parse out selected 1- or 2-cutter options
            $(this).closest('tbody').find('input[name|="cutters"]:checked').each(function () {
                if ($(this).attr('name')) {
                  var o = parseInt($(this).attr('name').match(/\d+/), 10);
                  opts.push(o);
                }
            });
            gd_map.redraw_cutters(opts);
        });
    }

    if (draw_layer_controls) {
        // Get list of layers
        layers = [];
        for (var i = 0; i < gd.all_features.length; i++) {
          layer = gd.all_features[i].layer();
          if (layers.indexOf(layer) < 0) { layers.push (layer); }
        }

        layer_control_table = 
            $('<tr><td class="layers">' +
              '<table><thead><tr><th>Show</th><th>Layer</th></tr>' + 
              '</thead><tbody></tbody></table></td></tr>')
            .appendTo(controls.find('.giraffe-controls-layout'))
            .find('tbody');

        for (li = 0; li < layers.length; li++) {
            var checked = ' checked="checked"';
            if (exclude_layers.indexOf(layers[li]) >= 0) {
                checked = '';
                gd_map.hide_feature_layer(layers[li]);
            }
            layer_control_table.append(
            '<tr>'+
                '<td><input type="checkbox" ' + checked +
                     ' data-layer="' + layers[li] + '" value="show" />' +
                '</td>' +
                '<td>' +  layers[li] + '</td></tr>');
        }

        // Changes to the feature types
        controls.find('td.layers input[value="show"]').click(function (event) {
            var layer_name;
            layer_name = $(this).attr("data-layer");
            if ($(this).is(":checked")) {
                gd_map.show_feature_layer(layer_name);
            } else {
                gd_map.hide_feature_layer(layer_name);
            }
        });
    }

    $(dom).append(controls);

    return controls;
};

})();

// vi: set expandtab:ts=4:sw=4:sts=4
