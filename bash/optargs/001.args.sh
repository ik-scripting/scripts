for _ in "$@"; do
    case $1 in
        -s|--script) SCRIPT="$2"; shift ;;
        -t|--target) TARGET="$2"; shift ;;
        -c|--configuration) CONFIGURATION="$2"; shift ;;
        -b|--buildconfiguration) BUILDCONFIGURATION="$2"; shift ;; # Added parameter
        -v|--verbosity) VERBOSITY="$2"; shift ;;
        -d|--dryrun) DRYRUN=true ;;
        --version) SHOW_VERSION=true ;;
    esac
    shift
done

# updated version

function k.get-list {
    usage() { echo "k.get-list: [--kind <resource kind> --api <api> --version <api version>]" 1>&2; }

    if [ "$#" -lt 6 ]; then
        echo "Not enough arguments... Should be '6' provided '$#'"
        usage
    else

        local kind api version
        for _ in "$@"; do
            case $1 in
                -k|--kind) kind="$2"; ;;
                -t|--api) api="$2"; ;;
                -c|--version) version="$2"; ;;
                --help) usage ;;
            esac
            shift
        done
        set -x
        kubectl get ${kind}.${version}.${api}
    fi
}
